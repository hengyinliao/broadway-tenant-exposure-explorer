"""Download official Vancouver open data and build a transparent Broadway research MVP."""
from pathlib import Path
import requests,json,csv,io,math,hashlib,datetime
from shapely.geometry import shape,Point,Polygon,mapping
from shapely.ops import transform
from shapely.strtree import STRtree
from pyproj import Transformer
import numpy as np

ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw';OUT=ROOT/'data/processed'
BASE='https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets'
BBOX=(-123.19,49.245,-123.065,49.275) # contextual study extent; not asserted as exact Plan boundary
STATIONS=[
 ('Great Northern Way–Emily Carr',49.2674,-123.0953),('Mount Pleasant',49.2629,-123.1001),
 ('Broadway–City Hall',49.2632,-123.1152),('Oak–VGH',49.2631,-123.1267),
 ('South Granville',49.2633,-123.1383),('Arbutus',49.2635,-123.1527)]
project=Transformer.from_crs(4326,26910,always_xy=True).transform

def download(ds,fmt='geojson',where=None):
    suffix='geojson' if fmt=='geojson' else 'csv';path=RAW/f'{ds}.{suffix}'
    if path.exists() and path.stat().st_size>1000:
        print('cached',ds,path.stat().st_size,flush=True);return path
    url=f'{BASE}/{ds}/exports/{fmt}?lang=en&timezone=America%2FVancouver'
    if where:url+='&where='+requests.utils.quote(where)
    r=requests.get(url,timeout=180);r.raise_for_status();path.write_bytes(r.content)
    (RAW/f'{ds}.manifest.json').write_text(json.dumps({'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(r.content).hexdigest(),'bytes':len(r.content)},indent=2))
    print(ds,len(r.content),flush=True);return path

def bounds(values):
    vals=np.array([v for v in values if v is not None and np.isfinite(v)])
    return tuple(np.percentile(vals,[5,95])) if len(vals)>=2 else (None,None)
def robust(bound,value):
    lo,hi=bound
    if value is None or lo is None:return None
    return round(float(np.clip((value-lo)/(hi-lo)*100,0,100)),1) if hi>lo else 50

def dist(a,b):return transform(project,a).distance(transform(project,b))

def build():
    RAW.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    parcels=json.loads(download('property-parcel-polygons').read_text(encoding='utf-8'))
    zoning=json.loads(download('zoning-districts-and-labels').read_text(encoding='utf-8'))
    permits=json.loads(download('issued-building-permits').read_text(encoding='utf-8'))
    nonmarket=json.loads(download('non-market-housing').read_text(encoding='utf-8'))
    tax=list(csv.DictReader(io.StringIO(download('property-tax-report','csv',"report_year='2025'").read_text(encoding='utf-8-sig')),delimiter=';'))
    extent=Polygon([(BBOX[0],BBOX[1]),(BBOX[2],BBOX[1]),(BBOX[2],BBOX[3]),(BBOX[0],BBOX[3])])
    ps=[]
    for f in parcels['features']:
        geom=shape(f['geometry']);pt=geom.representative_point()
        if extent.contains(pt):
            props=f['properties'];ps.append({'type':'Feature','geometry':mapping(geom),'properties':{'parcel_id':props.get('site_id') or props.get('tax_coord'),'tax_coord':props.get('tax_coord'),'address':f"{props.get('civic_number','')} {props.get('streetname','')}".strip(),'lon':pt.x,'lat':pt.y}})
    tax_by={}
    for r in tax:
        coord=r.get('LAND_COORDINATE') or r.get('land_coordinate')
        if not coord:continue
        # aggregate strata records so parcel-level totals are not one arbitrarily selected unit
        x=tax_by.setdefault(coord,{'land':0,'improvement':0,'year_built':[],'pid':[],'zoning':set(),'count':0})
        for key,target in [('CURRENT_LAND_VALUE','land'),('CURRENT_IMPROVEMENT_VALUE','improvement')]:
            raw=r.get(key) or r.get(key.lower())
            try:x[target]+=int(float(raw))
            except:pass
        y=r.get('YEAR_BUILT') or r.get('year_built')
        if y and str(y).isdigit():x['year_built'].append(int(y))
        x['pid'].append(r.get('PID') or r.get('pid'));x['zoning'].add(r.get('ZONING_DISTRICT') or r.get('zoning_district'));x['count']+=1
    zones=[]
    for f in zoning['features']:
        g=shape(f['geometry'])
        if g.intersects(extent):zones.append((g,f['properties']))
    zone_geoms=[g for g,_ in zones];zone_tree=STRtree(zone_geoms)
    permit_points=[]
    for f in permits['features']:
        if not f.get('geometry'):continue
        g=shape(f['geometry']);p=f['properties']
        if extent.contains(g) and str(p.get('issueyear',''))>='2017':permit_points.append((g,p))
    permit_geoms=[g for g,_ in permit_points];permit_tree=STRtree(permit_geoms)
    housing_points=[]
    for f in nonmarket['features']:
        if not f.get('geometry'):continue
        hg=shape(f['geometry'])
        if extent.contains(hg):housing_points.append((hg,f['properties']))
    housing_geoms=[g for g,_ in housing_points];housing_tree=STRtree(housing_geoms)
    ratios=[];ages=[];activity=[]
    for f in ps:
        p=f['properties'];g=shape(f['geometry']);t=tax_by.get(p['tax_coord']);
        if t:
            p['pid']=next((v for v in t['pid'] if v),None);p['land_value']=t['land'] or None;p['improvement_value']=t['improvement'] or None;p['year_built']=round(float(np.median(t['year_built']))) if t['year_built'] else None;p['assessment_year']=2025;p['assessment_record_count']=t['count']
            total=t['land']+t['improvement'];p['land_improvement_ratio']=round(t['land']/total,4) if total else None
        else:p.update({'pid':None,'land_value':None,'improvement_value':None,'year_built':None,'assessment_year':None,'assessment_record_count':0,'land_improvement_ratio':None})
        zone_hits=zone_tree.query(g.representative_point(),predicate='intersects');zone=zones[int(zone_hits[0])][1] if len(zone_hits) else None;p['current_zoning']=zone.get('zoning_district') if zone else None;p['zoning_classification']=zone.get('zoning_classification') if zone else None
        related=[]
        nearby=permit_tree.query(g.buffer(.00008),predicate='intersects')
        for permit_index in nearby:
            pg,permit=permit_points[int(permit_index)]
            if g.buffer(.00008).contains(pg):
                work=str(permit.get('typeofwork',''));desc=str(permit.get('projectdescription',''));kind='demolition' if 'demol' in (work+' '+desc).lower() else 'new construction' if 'new building' in (work+' '+desc).lower() or 'new construction' in (work+' '+desc).lower() else 'major alteration' if 'addition' in work.lower() or 'alteration' in work.lower() else 'other'
                if kind!='other':related.append({'permit_number':permit.get('permitnumber'),'issue_date':permit.get('issuedate'),'type':kind,'address':permit.get('address'),'description':desc[:300],'source_url':'https://opendata.vancouver.ca/explore/dataset/issued-building-permits/'})
        p['permits']=related;p['permit_count']=len(related);p['last_permit_year']=max([int(str(x['issue_date'])[:4]) for x in related if x['issue_date']],default=None)
        station,distance=min(((name,dist(Point(p['lon'],p['lat']),Point(lon,lat))) for name,lat,lon in STATIONS),key=lambda x:x[1]);p['nearest_station']=station;p['distance_station_m']=round(distance);p['within_400m']=distance<=400;p['within_800m']=distance<=800
        p['rental_status']='Unknown';p['rental_status_source']=None;p['existing_rental_units']=None;p['renter_exposure_score']=None;p['renter_exposure_status']='Unavailable — Census DA and confirmed rental inventory not integrated'
        housing=[]
        for housing_index in housing_tree.query(g.buffer(.00008),predicate='intersects'):
            hp,h=housing_points[int(housing_index)]
            if g.buffer(.00008).contains(hp):
                units=sum(int(h.get(k) or 0) for k in ('clientele_families','clientele_seniors','clientele_other'))
                housing.append({'index_number':h.get('index_number'),'name':h.get('name'),'status':h.get('project_status'),'occupancy_year':h.get('occupancy_year'),'operator':h.get('operator'),'units':units or None,'source_url':h.get('url')})
        p['non_market_housing_projects']=housing
        if housing:
            p['rental_status']='Confirmed non-market housing';p['rental_status_source']='City of Vancouver Non-market Housing inventory';p['existing_rental_units']=sum(x['units'] or 0 for x in housing) or None
        p['renter_exposure_status']='Unavailable — Census DA tenure not integrated; the non-market inventory is partial and absence of a match is not evidence of no renters'
        p['trpp_status']='Unknown';p['enhanced_protection_context']='Inside contextual Broadway study extent; project-level applicability requires case review'
        p['data_status']='derived_from_official_administrative_data';p['source_metadata']={'parcel':'City of Vancouver Property Parcel Polygons','assessment':'City of Vancouver Property Tax Report 2025','permits':'City of Vancouver Issued Building Permits','zoning':'City of Vancouver Zoning Districts and Labels','spatial_precision':'parcel geometry; permits matched by point-in/near parcel','confidence':'MEDIUM','manual_verification':False}
        ratio=p['land_improvement_ratio'];age=2025-p['year_built'] if p['year_built'] else None;act=min(100,40*sum(x['type']=='demolition' for x in related)+25*sum(x['type']=='new construction' for x in related)+10*sum(x['type']=='major alteration' for x in related))
        p['_age']=age;p['_activity']=act;ratios.append(ratio);ages.append(age);activity.append(act)
    ratio_bounds,age_bounds=bounds(ratios),bounds(ages)
    for f in ps:
        p=f['properties'];p['development_activity_score']=p.pop('_activity');p['land_value_score']=robust(ratio_bounds,p['land_improvement_ratio']);p['building_age_score']=robust(age_bounds,p.pop('_age'));p['station_proximity_score']=round(100*math.exp(-p['distance_station_m']/600),1)
        # Current zoning category is shown; policy potential remains unavailable without a verified Broadway schedule geometry.
        p['policy_potential_score']=None;p['policy_potential_status']='Unavailable — verified parcel-level Broadway policy schedule not integrated'
        available=[(p['development_activity_score'],.30),(p['land_value_score'],.20),(p['building_age_score'],.15),(p['station_proximity_score'],.10)]
        p['redevelopment_pressure_score']=round(sum(v*w for v,w in available if v is not None)/sum(w for v,w in available if v is not None),1) if all(v is not None for v,w in available) else None
        p['pressure_data_completeness']=round(sum(w for v,w in available if v is not None)/.75,2);p['exposure_category']='Unavailable — renter exposure missing';p['tenant_redevelopment_exposure_score']=None
    station_features=[]
    for name,lat,lon in STATIONS:station_features.append({'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},'properties':{'name':name,'source':'Broadway Subway Project / Government of BC','source_url':'https://www.broadwaysubway.ca/about/stations/','status':'under construction'}})
    meta={'title':'Broadway Tenant Redevelopment Exposure Explorer','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'study_extent_status':'proxy','study_extent_note':'Contextual rectangle based on City description: Vine to Clark, 1st to 16th. It is not the official legal/policy boundary.','weights':{'development_activity':30,'policy_potential':25,'land_value_intensity':20,'building_age':15,'station_proximity':10},'claims':'Spatial overlap and exploratory pressure only; no causal or displacement outcome claim.'}
    data={'type':'FeatureCollection','metadata':meta,'stations':station_features,'study_extent':mapping(extent),'features':ps}
    for path in [OUT/'broadway_parcels.geojson',ROOT/'frontend/public/data/broadway_parcels.geojson']:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
    print('built',len(ps),'parcels',len(permit_points),'permit points')
if __name__=='__main__':build()
