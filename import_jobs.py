#!/usr/bin/env python3
"""
Import Jobs into Scaffolding Business Database
Fixed version that matches your current schema
"""

import sqlite3
import os
import re
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.expanduser('~'), 'scaffolding_business.db')

# Areas mapping
AREA_MAPPING = {
    'peterborough': 'Peterborough',
    'leicester': 'Leicester',
    'london': 'London',
    'birmingham': 'Birmingham',
    'bhm': 'Birmingham'
}

def extract_postcode(address):
    """Extract UK postcode from address"""
    pattern = r'\b([A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2})\b'
    match = re.search(pattern, address.upper())
    if match:
        return match.group(1)
    return ''

def parse_date(date_str):
    """Parse date string to YYYY-MM-DD format"""
    try:
        date_obj = datetime.strptime(date_str.strip(), '%m/%d/%Y')
        return date_obj.strftime('%Y-%m-%d')
    except:
        return date_str.strip()

def map_status(status_str):
    """Map status from CSV to database status"""
    status = status_str.lower().strip()
    if status == 'removed':
        return 'completed'
    elif status == 'done':
        return 'active'
    else:
        return 'pending'

def generate_job_number(index, area):
    """Generate unique job number"""
    prefix = {
        'Peterborough': 'PB',
        'Leicester': 'LC',
        'London': 'LD',
        'Birmingham': 'BH'
    }.get(area, 'JB')
    return f"{prefix}{str(index + 1000).zfill(5)}"

def parse_jobs():
    """Parse all job data"""
    jobs = []
    
    # Peterborough jobs
    peterborough_data = """
9/10/2024,u shape,1 holdich st pe3 6dh,1000,removed,karan
9/13/2024,u shape,64 exeter rd pe1 3qa,1000,removed,karan
9/13/2024,front back,148 gladstone st pe1 2bl,800,removed,karan
9/16/2024,u shape,117 palmerston rd woodston pe2 9de,1000,removed,jandu
9/17/2024,u shape back te l,34 williamson ave pe3 6ba,1200,removed,karan
9/17/2024,u shape,3 holdich st pe3 6dh,1000,removed,karan
9/18/2024,front back,22 kent rd pe3 6dg,800,removed,karan
9/18/2024,front back,133 eastfield rd pe1 4au,800,removed,karan
9/19/2024,front back,42 windmill st pe1 2lu,800,removed,karan
9/19/2024,front back,136 clarence rd pe1 2le,800,removed,karan
9/19/2024,front back,70 star rd pe1 5hl,800,removed,karan
9/19/2024,front back,22 stone ln pe1 3bn,800,removed,karan
9/20/2024,u shape back te l+bridge,51 russell street pe1 2bj,1300,removed,karan
9/20/2024,u shape,198 st pauls rd pe1 3ef,1000,removed,karan
9/21/2024,front back,72 russell st pe1 2bj,800,removed,jandu
9/21/2024,front back,58 bamber st pe12hn,800,removed,jandu
9/21/2024,front back,74 st martin st pe1 3bd,800,removed,karan
9/21/2024,front back,191 st pauls rd pe1 3ed,800,removed,karan
9/21/2024,front back,3 fengate close pe1 5ar,800,removed,karan
9/23/2024,front back,819 lincoln rd pe1 3hg,800,removed,karan
9/23/2024,front back,31 russel st pe1 2bq,800,removed,karan
9/23/2024,u shape,40 whally st pe1 5eb,1000,removed,karan
9/24/2024,front back,40 windmill st pe1 2lu,800,removed,karan
9/24/2024,front back,30 clarence rd pe1 2la,800,removed,karan
9/24/2024,u shape,192 crown st pe1 3ja,1000,removed,karan
9/25/2024,l shape,1 hereward close pe1 5an,900,removed,satwant
9/25/2024,front back,130 st pauls rd pe1 3dp,700,removed,satwant
9/25/2024,front back,29 bamber st pe1 2hn,700,removed,satwant
9/25/2024,front back,19 bedford st pe1 4dn,700,removed,satwant
9/25/2024,front back,763 lincoln rd pe1 3he,700,removed,satwant
9/25/2024,front,42 silverwoood rd pe1 2jf,500,removed,satwant
9/26/2024,front back,48 granville st pe1 2qj,800,removed,karan
9/26/2024,front,61 sallows rd pe1 4ex,500,removed,karan
9/26/2024,front back,837 lincoln rd pe1 3hg,700,removed,karan
9/27/2024,front back,90 st martins st pe1 3bd,700,removed,lavi prince
10/1/2024,front back,40 burmer rd pe1 3hu,700,removed,satwant
10/1/2024,front back,757 lincoln rd pe1 3he,700,removed,satwant
10/1/2024,front back,273 cromwell rd pe1 2hq,700,removed,satwant
10/1/2024,front,33 sumerfield rd pe1 2jd,500,removed,satwant
10/2/2024,u shape back l,10 highbury street pe1 3be,1200,removed,karan
10/2/2024,u back back l,81 scotney st pe1 3ne,1200,removed,karan
10/3/2024,u shape baclk l,175 crown street pe1 3ja,1200,removed,karan
10/3/2024,u shape,1 st james avenue pe1 3js,1000,removed,karan
10/4/2024,front,45 percival st pe3 6au,500,removed,karan
10/4/2024,u shape back l,72 thistlemoor rd pe1 3hp,1200,removed,karan
10/5/2024,u shape back l,20highbury street pe1 3be,1200,removed,karan
10/5/2024,front back,41 highbury street pe1 3be,700,removed,karan
10/5/2024,front back,127a aldermans drive pe3 6az,700,removed,karan
10/7/2024,l shape extiton,192 crown st pe1 3ja,900,removed,karan
10/7/2024,u shape,59 allen rd pe1 3bt,1000,removed,karan
10/7/2024,u shape,2 almoners ln pe3 9eh,1000,removed,karan
10/7/2024,u shape baclk l,41 morris st pe1 5dx,1200,removed,karan
10/8/2024,u shape back l,134 cromwell rd pe1 2eu,1200,removed,karan
10/8/2024,u shape,7 eastgate pe1 5bs,1000,removed,karan
10/9/2024,front back,47 percival st pe3 6at,700,removed,jandu
10/10/2024,u shape back l,173 crown st pe1 3ja,1200,removed,karan
10/10/2024,front back,3 occupation rd pe1 2dh,800,removed,karan
10/11/2024,u shape back l,7 scotney st pe1 3ng,1200,removed,karan
10/11/2024,l shape,50 crown st pe1 3hy,900,removed,karan
10/12/2024,front,135 gladstone pe1 2bn,500,removed,karan
10/12/2024,front back,74 dogsthorpe pe1 3aq,700,removed,karan
10/12/2024,front back,159 queens walk pe2 9aj,700,removed,karan
10/12/2024,front back,94 alma road pe1 3aw,700,removed,karan
10/14/2024,u shape back l,225 star rd pe1 5et,1200,removed,karan
10/15/2024,front back,12 montagu rd pe4 6ee,700,removed,lavi
10/16/2024,front back,228 gladstone st pe1 2bp,700,removed,karan
10/16/2024,front back,140 crown st pe1 3hz,700,removed,karan
10/16/2024,front back,43 highbury st pe1 3be,700,removed,karan
10/16/2024,l shape,5 elmfield rd pe1 4ha,900,removed,karan
10/17/2024,u shape baclk l,922 bourges blvd pe1 2an,1200,removed,jarman
10/17/2024,front back,31 holdich st pe3 6dh,700,removed,karan
10/17/2024,front back,63 scotney st pe1 3ne,700,removed,karan
10/17/2024,front back,17 morris st pe1 5dx,700,removed,karan
10/18/2024,front back,61 midland rd pe3 6dd,700,removed,karan
10/18/2024,front back,127 wellington st pe1 5du,700,removed,karan
10/18/2024,front,52 whitsed st pe1 5ed,500,removed,karan
10/19/2024,l shape,40 st james ave,900,removed,karan
10/19/2024,u shape,91 grange rd pe3 9dz,1000,removed,karan
10/21/2024,u shape back l,48 mayors walk pe3 6et,1200,removed,karan
10/21/2024,u shape back l,100 aldermans dr pe3 6az,1200,removed,karan
10/22/2024,u shape back l,54 mayore walk pe3 6et,1200,removed,karan
10/22/2024,u shape back l,56 mayore walk pe3 6et,1200,removed,karan
10/23/2024,front back,689 lincoln road pe1 3hd,700,removed,karan
10/23/2024,front back,47 midland road pe3 6dd,700,removed,karan
10/24/2024,l shape,3 eastleigh rd pe1 5jq,900,removed,prince
10/24/2024,l shape,105 northfield rd pe1 3qf,900,removed,prince
10/25/2024,l shape,12 nicholls ave pe3 9el,900,removed,prince
10/25/2024,front back,106 belsize ave pe2 9ja,700,removed,prince
10/25/2024,front back,79 clarence rd pe1 2lb,700,removed,prince
10/25/2024,front back,272 clarence rd pe1 2lq,700,removed,prince
10/26/2024,front back,398 lincoln rd pe1 2na,700,removed,prince
10/26/2024,front back,51 gladstone st pe1 2be,700,removed,prince
10/26/2024,front back,83 princes st pe1 2qp,700,removed,prince
10/28/2024,l shape,14 lawn ave pe1 3rb,900,removed,prince
10/28/2024,u shape,124 fengate pe1 5bb,1000,removed,prince
10/28/2024,front back,70 st margarets pl pe2 9eb,700,removed,prince
10/29/2024,front back,123 gladstone st pe1 2bn,700,removed,prince
10/29/2024,front back,35 craig st pe1 2ej,700,removed,prince
10/29/2024,front back,84 russell st pe1 2bj,700,removed,prince
10/30/2024,front back,54 montagu rd pe4 6ep,700,removed,prince
10/30/2024,front back,39 monument st pe1 4ag,700,removed,prince
10/31/2024,front,114 churchfield rd pe4 6he,500,removed,prince
10/31/2024,front back,230 gladstone st pe1 2bp,700,removed,prince
10/31/2024,front back,143 huntly grove pe1 2qw,700,removed,prince
11/1/2024,front back,761 lincoln rd pe1 3he,700,removed,prince
11/1/2024,front back,94 granville st pe1 2qj,700,removed,prince
11/4/2024,l shape,47 glenton st pe1 5hh,900,removed,prince
11/5/2024,l shape,159 newark ave pe1 4nl,900,removed,karan
11/5/2024,front back,154 crown st pe1 3hz,700,removed,karan
11/7/2024,front back,66 all saints rd pe1 2qu,700,removed,prince
11/7/2024,u shape back l,685 lincoln rd pe1 3hd,1200,removed,prince
11/8/2024,u shape back l,153 wellington st pe1 5du,1200,removed,prince
11/8/2024,u shape,39 edwalton ave pe3 6er,1000,removed,prince
11/9/2024,u shape,50 padholme rd pe1 5ee,1000,removed,prince
11/9/2024,u shape,185 gladstone st pe1 2bn,1000,removed,prince
11/11/2024,u shape,31 princes gardens pe1 4dp,1000,removed,prince
11/12/2024,u shape back l,107 aldermans dr pe3 6az,1200,removed,prince
11/12/2024,u shape,5 hereward rd pe1 5al,1000,removed,prince
11/13/2024,u shape back l,687 lincoln rd pe1 3hd,1200,removed,prince
11/14/2024,u -shape,135 northfield road pe1 3qf,1000,removed,lavi
11/14/2024,u- shape + back-l,582 gladstone street pe1 2dg,1200,removed,lavi
11/15/2024,front back,693 lincoln rd pe1 3hd,700,removed,lavi
11/15/2024,u shape,44 churchfield rd pe4 6he,1000,removed,lavi
11/16/2024,l shape,54 peveril rd pe1 3ps,900,removed,lavi
11/16/2024,front back,23 thistlemoor rd pe1 3hr,700,removed,lavi
11/17/2024,u shape back l big job,127 palmerston rd pe2 9de,1600,removed,arsh
11/19/2024,front back,13 monument st pe1 4aq,700,removed,noori
11/19/2024,l shape,47 northfield rd pe1 3qg,900,removed,noori
11/20/2024,front back,33 craig st pe1 2ej,700,removed,noori
11/20/2024,l shape,98 thistlemoor rd pe1 3hp,900,removed,noori
11/20/2024,u shape,16 edwalton avenue pe3 6er,1000,removed,jandu
11/20/2024,l shape,26 springfield rd pe1 2jg,900,removed,jandu
11/20/2024,u shape,21 ashcroft gardens pe1 5lp,1000,removed,noori
11/21/2024,u shape back l,135 aldermans drive pe3 6bb,1200,removed,noori
11/22/2024,front back,49 northfield rd pe1 3qg,700,removed,
11/22/2024,u shape back l,4 vergetle st pe1 4dl,1200,removed,
11/22/2024,front back,70 all saints rd pe1 2qu,700,removed,
11/23/2024,front back,52 gladstone st pe1 2bd,700,removed,
11/25/2024,u shape,9 northfield rd pe1 3qq,1000,removed,jandu
11/26/2024,u shape,108 st pauls rd pe1 3dp,1000,removed,karan
11/28/2024,u shape back l,98 vere rd pe1 3ea,1200,removed,karan
11/28/2024,u shape back l,113 harris st pe1 2lz,1200,removed,karan
11/30/2024,front back,179 eastfield rd pe1 4bh,700,removed,noori
11/30/2024,u shape back l,13 church walk pe1 2tp,1200,removed,noori
12/4/2024,u shape back l,517 gladstone st pe1 2dq,1200,removed,lavi
12/9/2024,u shape,35 st james ave pe1 3js,1000,removed,jandu
12/9/2024,u shape back l,54 st pauls rd pe1 3dw,1200,removed,jandu
1/7/2025,u shape,18 gunthorpe rd pe4 7tg,1000,removed,noori
1/7/2025,side,353 gladstone st pe1 2da,400,removed,noori
2/15/2025,side,24 williamson avenue west town pe3 6ba,400,removed,
3/11/2025,front back,5 clifton avenue pe3 6ay,800,removed,
3/19/2025,l shape,47 vere rd pe1 3eb,900,removed,anmol
3/21/2025,u shape,49 peveril rd pe1 3px,1000,removed,anmol
4/10/2025,u shape,16 grimshaw rd pe1 4et,1000,removed,anmol
6/23/2025,u shape,39 priory rd pe3 9ed,1000,removed,anmol
8/18/2025,front back double,28 burghley road pe1 2qb,1000,removed,
8/18/2025,front back double,57 montagu road pe4 6ee,1000,done,
8/20/2025,front back l double,119 st pauls road pe1 3dr,1100,removed,
8/20/2025,u shape double gavel,9 allen road pe1 3bt,1300,done,
8/20/2025,u shape double gavel,4 nicholls avenue pe3 9el,1300,removed,
8/22/2025,front,125 lok road pe30 2bg,500,removed,
8/22/2025,u shape back l big job,11 horsegate lane pe7 1jn,1600,done,
8/29/2025,u shape double,57 allen road pe1 3bt,1200,removed,
8/29/2025,u shape double,91 palmerston road pe2 9de,1200,removed,
9/6/2025,u shape double gavel,89 elmfield road pe1 4ha,1300,removed,
9/12/2025,u shape back l big job,1096 bourges blvd pe1 2aw,1600,done,karan
9/12/2025,front back l double,78 princes st pe1 2ps,1100,done,karan
9/15/2025,u shape double base,36 st james ave pe1 3jr,900,removed,jandu
9/15/2025,front back l double,53 fengate pe1 5ba,900,done,jandu
9/15/2025,u shape back l,1058 bourges blvd pe1 2aw,1100,done,jandu
10/1/2025,front back l double,13 parliament st pe1 2ls,900,done,jandu
10/1/2025,u shape,37 priory road pe3 9ed,900,done,jandu
10/9/2025,front back l double,47 scotney st pe1 3ng,900,done,
10/16/2025,u shape,126 garton end road pe1 4ez,900,done,anmol
10/18/2025,front back l double,79 harris st pe1 2lz,900,done,anmol
10/20/2025,u shape back l,42 lime tree ave pe1 2ns,1200,done,anmol
"""
     # Leicester jobs
    leicester_data = """
11/23/2024,front back,99 wand st le4 5bu,700,removed,jandu
11/23/2024,u shape,54 scarborough rd le4 6pf,1000,removed,jandu
11/23/2024,u shape,56 scarborough rd le4 6pf,1000,removed,jandu
11/25/2024,front,79 church hill rd le4 8df,500,removed,noori
11/26/2024,front back,74 down st le4 6je,700,removed,karan
11/26/2024,front back,6 bardolph st le4 6ef,700,removed,karan
11/27/2024,u shape,20 oliver rd le4 7gq,1000,removed,karan
11/27/2024,l shape,92 freeman rd n rowlatts hill le5 4na,900,removed,karan
11/28/2024,u shape,13 headland rd le5 6ae,1000,removed,noori
11/28/2024,u shape back l,3 draper st le2 1pq,1200,removed,noori
11/29/2024,u shape back l,20 bride rd le5 3la,0,removed,noori
11/29/2024,front back,45 bardolph st le4 6eh,700,removed,noori
12/3/2024,u shape,304 humberstone ln le4 6an,1000,removed,noori
12/3/2024,front back,70 burfield st le4 6an,700,removed,noori
12/6/2024,l shape,613 saffron ln le2 6un,900,removed,lavi
3/19/2025,back one step after babbu finished,51 hayness rd le5 4ar,400,removed,
3/20/2025,front back,10 duxbury rd le5 3lq,800,removed,
"""

    # London jobs
    london_data = """
12/7/2024,u shape gutar leval,3 amersham ave london n18 1ds,1600,removed,jaramn
"""   
    
    # Birmingham jobs
    birmingham_data = """
12/19/2024,front back,24 molesworth avenue cv3 1bu,0,removed,jarman
12/19/2024,front back,735 warwick rd b11 2ha,0,removed,jarman
12/19/2024,front back,97 white rd b67 7pq,0,removed,jarman
12/24/2024,front back,217 churchill rd b9 5nx,0,removed,jarman
1/13/2025,front back L,737 warwick rd tyseley b11 2ha,800,removed,jarman
1/13/2025,front back u double base,18 weatheroak rd b11 4re,950,removed,jarman
1/13/2025,front back L,24 brandon rd b28 8dx,800,removed,jarman
5/27/2025,front back l double,128 village rd b6 6rd,1100,removed,jandu
5/27/2025,u shape,10 flavells lane b25 8sg,1000,removed,jandu
5/27/2025,u shape double base,98 burney lane ward end b8 2ar,1200,done,jandu
6/12/2025,u shape double base,95 white rd b67 7pq,1200,removed,jandu
6/12/2025,fronr back l double base,28 somerville rd b10 9el,1100,done,jandu
6/14/2025,fronr back l double base,52 medicott road b11 1py,1100,removed,jarman
6/14/2025,u shape,532 fox hollies rd b28 8rw,1000,removed,jarman
6/17/2025,front back l double,66 baptist end rd dy2 9dj,1000,removed,jandu
6/17/2025,front back,71 erdington hall rd b24 8jn,800,done,jandu
6/23/2025,front back l double,49 thornbury rd b20 3de,1100,done,jarman
6/23/2025,u shape,324 dyas rd b44 8td,1000,removed,jarman
6/23/2025,front back l double,47 farnham rd b21 8eq,1100,removed,jarman
6/25/2025,front back l double,99 waterloo street de14 2nd,1100,removed,jandu
6/25/2025,big jojb u shape back l,144 dale street ws1 4ax,1600,removed,jandu
7/9/2025,u shape double base,72 rectory park road b26 3lh,1200,done,jandu
7/9/2025,u shape back l,212 malmesbury road b10 0jj,1600,done,jandu
7/9/2025,front double back,19 giles rd oldbury,900,removed,jandu
7/11/2025,u shape,7 hugh road smethwick b67 7ju,1000,done,jandu
7/16/2025,front back l double,25 deykin ave witton b6 7be,1100,done,karan
7/16/2025,u shape double base,134 highfield road b28 0hu,1200,removed,karan
7/17/2025,front back,50 hartlepool road cv1 5ja,900,done,jandu
7/22/2025,u shape double base,71 circuler rd b27 7db,1200,removed,karan
7/22/2025,front back l double,57 lilly road b26 1te,1100,removed,karan
7/22/2025,front back double,9 way ave b12 8rg,1000,done,karan
7/25/2025,front back,8 treaford ln b8 2ug,800,done,karan
7/25/2025,front back double,3 the elms marroway b16 0az,1000,done,karan
7/29/2025,front back l double,117 formans rd b11 3ax,1100,done,jandu
7/31/2025,l l shape,18 hutton road handworth b20 3rb,1400,done,dhindsa
7/31/2025,front back l double,64 kentish rd b21 0ax,1100,removed,dhindsa
8/1/2025,front back l double,40 bennetts rd saltley b8 1qh,1100,done,dhindsa
8/2/2025,front back l double,80 clarence rd de23 6lq,1100,done,jandu
8/2/2025,front back double,27 leicester st wv6 0pr,1000,removed,jandu
8/11/2025,front back l,136 anglesey road de14 3nt,1100,removed,dhindsa
8/13/2025,u shape back l,63 cope st bloxwich walsall,1600,done,jandu
8/14/2025,u shape double base,41 blake ln b9 5qt,1200,done,jandu
8/14/2025,u shape double base,43 blake ln b9 5qt,1200,done,jandu
8/19/2025,u shape back l,1 rosary villas b11 1ul,1600,done,
8/22/2025,front back l double,82 haddon st de23 6nq,1100,done,
8/29/2025,u shape double base,33 malmesbury rd b10 0jg,1200,done,
8/2/2025,u shape double gavel,32 gervase dr dy1 4at,1300,done,
8/2/2025,front back l double,149 w bromwich rd ws1 3hp,1100,done,
8/2/2025,front back l double,122 kentish rd b21 0ba,1100,done,
8/3/2025,front back,88 greenwood ave b27 7rd,900,done,
8/3/2025,front back l double,60 wattville road b21 0dr,1100,removed,
9/10/2025,front back l double,35 gordon st de14 2hz,1100,done,
10/13/2025,front back l double,98 victoria st de14 2ls,1100,done,dhindsa
10/13/2025,u shape back l,111 oldknow road b10 0ja,1600,done,dhindsa
"""
    
    datasets = [
        ('Peterborough', peterborough_data),
        ('Leicester', leicester_data),
        ('London', london_data),
        ('Birmingham', birmingham_data)
    ]
    
    for area, data in datasets:
        for line in data.strip().split('\n'):
            if not line.strip():
                continue
                
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 5:
                continue
            
            date_str = parse_date(parts[0])
            job_type = parts[1]
            address = parts[2]
            price = float(parts[3]) if parts[3] and parts[3] != '0' else 0
            status = map_status(parts[4])
            fitter = parts[5] if len(parts) > 5 else ''
            
            job = {
                'date': date_str,
                'jobType': job_type,
                'address': address,
                'area': area,
                'price': price,
                'status': status,
                'fitter': fitter
            }
            jobs.append(job)
    
    return jobs

def import_jobs_to_db():
    """Import jobs into the database"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("Please run the main application first to create the database.")
        return
    
    print("=" * 60)
    print("  SCAFFOLDING BUSINESS - JOB IMPORT TOOL")
    print("=" * 60)
    print()
    print(f"📂 Database: {DB_PATH}")
    print()
    
    # Parse jobs
    print("📋 Parsing job data...")
    jobs = parse_jobs()
    print(f"✅ Found {len(jobs)} jobs to import")
    print()
    
    # Show breakdown by area
    area_counts = {}
    for job in jobs:
        area = job['area']
        area_counts[area] = area_counts.get(area, 0) + 1
    
    print("📊 Jobs by area:")
    for area, count in sorted(area_counts.items()):
        print(f"   • {area}: {count} jobs")
    print()
    
    # Ask for confirmation
    response = input("Do you want to import these jobs? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Import cancelled")
        return
    
    # Import to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    imported = 0
    skipped = 0
    
    print()
    print("📥 Importing jobs...")
    
    for i, job in enumerate(jobs):
        job_number = generate_job_number(i, job['area'])
        
        try:
            cursor.execute('''
                INSERT INTO jobs (
                    jobNumber, clientName, location, area, jobType,
                    startDate, status, value, notes,
                    createdAt, updatedAt
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (
                job_number,
                f"Client at {job['address'][:30]}...",  # Use address as client name
                job['address'],
                job['area'],
                job['jobType'],
                job['date'],
                job['status'],
                job['price'],
                f"Fitter: {job['fitter']}" if job['fitter'] else None
            ))
            imported += 1
            
            if imported % 10 == 0:
                print(f"   ✓ Imported {imported} jobs...")
                
        except sqlite3.IntegrityError:
            skipped += 1
            continue
        except Exception as e:
            print(f"   ⚠️ Error importing job {job_number}: {e}")
            skipped += 1
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 60)
    print(f"✅ Import complete!")
    print(f"   • Successfully imported: {imported} jobs")
    if skipped > 0:
        print(f"   • Skipped (duplicates/errors): {skipped} jobs")
    print("=" * 60)
    print()

if __name__ == '__main__':
    import_jobs_to_db()
    input("Press Enter to exit...")