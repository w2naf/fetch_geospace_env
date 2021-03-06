#!/usr/bin/env python3
import datetime
import numpy as np
import pandas as pd
from collections import OrderedDict
import bz2

#year,doy,hr,B_nT,Bx_GSE_nT,By_GSM_nT,Bz_GSM_nT,T_K,P,V,Kp_x10,R,Dst_nT,Ap_nT,F10.7,AE,AL,AU,Pc,Lyman_alpha
#year,doy,hr,P,V,Kp_x10,R,Dst_nT,Ap_nT,F10.7,AE,AL,AU,Pc,Lyman_alpha

vrs = OrderedDict()
vrs['YEAR'] = {'name':'year'}
vrs['DOY']  = {'name':'doy'}
vrs['HR']   = {'name':'hr'}

vrs['Bartels rotation number']          = {'symbol':'bartels'}
vrs['ID for IMF spacecraft']            = {'symbol':'IMF_spacecraft_ID'}
vrs['ID for SW Plasma spacecraft']      = {'symbol':'SW_spacecraft_ID'}
vrs['# of points in IMF averages']      = {'symbol':'N_IMF_points'}
vrs['# of points in Plasma averag.']    = {'symbol':'N_plasma_points'}
vrs['Scalar B, nT']                     = {'symbol':'B_nT'}
vrs['Vector B Magnitude,nT']            = {'symbol':'B_vec_nT'}
vrs['Lat. Angle of B (GSE)']            = {'symbol':'B_theta_GSE'}
vrs['Long. Angle of B (GSE)']           = {'symbol':'B_phi_GSE'}
vrs['BX, nT (GSE, GSM)']                = {'symbol':'Bx_GSE_nT'}
vrs['BY, nT (GSE)']                     = {'symbol':'By_GSE_nT'}
vrs['BZ, nT (GSE)']                     = {'symbol':'Bz_GSE_nT'}
vrs['BY, nT (GSM)']                     = {'symbol':'By_GSM_nT'}
vrs['BZ, nT (GSM)']                     = {'symbol':'Bz_GSM_nT'}
vrs['RMS_magnitude, nT']                = {'symbol':'RMS_mag_nT'}
vrs['RMS_field_vector, nT']             = {'symbol':'RMS_vec_nT'}
vrs['RMS_BX_GSE, nT']                   = {'symbol':'RMS_BX_GSE_nT'}
vrs['RMS_BY_GSE, nT']                   = {'symbol':'RMS_BY_GSE_nT'}
vrs['RMS_BZ_GSE, nT']                   = {'symbol':'RMS_BZ_GSE_nT'}
vrs['SW Plasma Temperature, K']         = {'symbol':'T_K'}
vrs['SW Proton Density, N/cm^3']        = {'symbol':'N_p'}
vrs['SW Plasma Speed, km/s']            = {'symbol':'V'}
vrs['SW Plasma flow long. angle']       = {'symbol':'SW_phi'}
vrs['SW Plasma flow lat. angle']        = {'symbol':'SW_theta'}
vrs['Alpha/Prot. ratio']                = {'symbol':'alpha_prot_ratio'}
vrs['sigma-T,K']                        = {'symbol':'sigma_T_K'}
vrs['sigma-n, N/cm^3)']                 = {'symbol':'sigma_N_p'}
vrs['sigma-V, km/s']                    = {'symbol':'sigma_V'}
vrs['sigma-phi V, degrees']             = {'symbol':'sigma_phi'}
vrs['sigma-theta V, degrees']           = {'symbol':'sigma_theta'}
vrs['sigma-ratio']                      = {'symbol':'sigma_ratio'}
vrs['Flow pressure']                    = {'symbol':'P'}
vrs['E elecrtric field']                = {'symbol':'E'}
vrs['Plasma betta']                     = {'symbol':'beta'}
vrs['Alfen mach number']                = {'symbol':'M_alfven'}
vrs['Magnetosonic Much num.']           = {'symbol':'M_magsonic'}
vrs['Kp index']                         = {'symbol':'Kp_x10'}
vrs['R (Sunspot No.)']                  = {'symbol':'R'}
vrs['Dst-index, nT']                    = {'symbol':'Dst_nT'}
vrs['ap_index, nT']                     = {'symbol':'Ap_nT'}
vrs['f10.7_index']                      = {'symbol':'F10.7'}
vrs['AE-index, nT']                     = {'symbol':'AE'}
vrs['AL-index, nT']                     = {'symbol':'AL'}
vrs['AU-index, nT']                     = {'symbol':'AU'}
vrs['pc-index']                         = {'symbol':'Pc','NaN':999.9}
vrs['Lyman_alpha']                      = {'symbol':'Lyman_alpha'}
vrs['Proton flux (>1 Mev)']             = {'symbol':'PF_1MeV','NaN':999999.99}
vrs['Proton flux (>2 Mev)']             = {'symbol':'PF_2MeV','NaN':99999.99}
vrs['Proton flux (>4 Mev)']             = {'symbol':'PF_4MeV','NaN':99999.99}
vrs['Proton flux (>10 Mev)']            = {'symbol':'PF_10MeV','NaN':99999.99}
vrs['Proton flux (>30 Mev)']            = {'symbol':'PF_30MeV','NaN':99999.99}
vrs['Proton flux (>60 Mev)']            = {'symbol':'PF_60MeV','NaN':99999.99}
vrs['Flux FLAG']                        = {'symbol':'flux_flag'}

def date_parser(row):
    year    = row['year']
    doy     = row['doy']
    hr      = row['hr']

    dt  = datetime.datetime(int(year),1,1)+datetime.timedelta(days=(int(doy)-1),hours=int(hr))
    return dt

def load_pandas(input_file):

    # Open File
    if input_file[-4:] == '.bz2':
        with bz2.BZ2File(input_file) as fl:
            lines   = fl.readlines()
        lines   = [x.decode() for x in lines]

    else:
        with open(input_file) as fl:
            lines   = fl.readlines()
    
    # Pull out data, ignore headers and footers.
    data    = []
    names   = OrderedDict()
    for line in lines:
        ln  = line.split()
        try:
            if ln[0] == 'YEAR':
                cols = ln
                continue

            col0 = int(ln[0])
            if col0 > 1800:
                data.append(ln)
            else:
                names[col0] = ' '.join(ln[1:])
        except:
            pass

    # Get a dictionary that only has the variables in the actual datafile.
    columns = ['year','doy','hr']
    nan_dct = OrderedDict()
    for key,val in names.items():
        result = vrs.get(val)
        if result is None:
            symbol = key
        else:
            symbol          = result['symbol']
            nan_dct[symbol] = result.get('NaN')
        columns.append(symbol)

    # Place into dataframe.
    df          = pd.DataFrame(data,columns=columns,dtype=np.float)

    # Parse Dates and remove old date columns
    df.index    = df.apply(date_parser,axis=1)
    del df['year']
    del df['doy']
    del df['hr']

    # Remove Not-a-Numbers
    for key,val in nan_dct.items():
        if val is not None:
            tf  = df[key] == val
            df.loc[tf,key]  = np.nan

    # Scale Kp
    df['Kp']   = df['Kp_x10']/10.
    del df['Kp_x10']

    return df
    
if __name__ == '__main__':
    input_file  = 'omni_data.txt'
    df          = load_pandas(input_file)
