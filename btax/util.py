from __future__ import unicode_literals
from collections import OrderedDict, defaultdict
import numbers
import os
from pkg_resources import resource_stream, Requirement

import pandas as pd

# Default year for model runs
DEFAULT_START_YEAR = 2017

def to_str(x):
    if hasattr(x, 'decode'):
        return x.decode()
    return x

def read_from_egg(tfile):
    '''Read a relative path, getting the contents
    locally or from the installed egg, parsing the contents
    based on file_type if given, such as yaml
    Params:
        tfile: relative package path
        file_type: file extension such as "json" or "yaml" or None

    Returns:
        contents: yaml or json loaded or raw
    '''
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), tfile)
    if not os.path.exists(template_path):
        path_in_egg = os.path.join("btax", tfile)
        buf = resource_stream(Requirement.parse("btax"), path_in_egg)
        _bytes = buf.read()
        contents = str(_bytes)
    else:
        with open(template_path, 'r') as f:
            contents = f.read()
    return contents

def get_paths():
    paths = {}
    _CUR_DIR = _MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
    _DATA_DIR = os.path.join(_MAIN_DIR, 'data')
    paths['_MAIN_DIR'] = paths['_DATA_DIR'] = _MAIN_DIR
    paths['_RATE_DIR'] = _RATE_DIR = os.path.join(_DATA_DIR, 'depreciation_rates')
    paths['_REF_DIR'] = os.path.join(_DATA_DIR, 'reference_data')
    paths['_RAW_DIR'] = _RAW_DIR = os.path.join(_DATA_DIR, 'raw_data')
    paths['_DEPR_DIR'] = _DEPR_DIR = os.path.join(_DATA_DIR, 'depreciation_rates')
    paths['_BEA_DIR'] = _BEA_DIR = os.path.join(_RAW_DIR, 'BEA')
    paths['_FIN_ACCT_DIR'] = _FIN_ACCT_DIR = os.path.join(_RAW_DIR, 'national_accounts')
    paths['_OUT_DIR'] = os.environ.get('BTAX_OUT_DIR', 'btax_output_dir')
    if not os.path.exists(paths['_OUT_DIR']):
        os.mkdir(paths['_OUT_DIR'])
    paths['_BEA_ASSET_PATH'] = _BEA_ASSET_PATH = os.path.join(_BEA_DIR, "detailnonres_stk1.xlsx")
    paths['_SOI_BEA_CROSS'] = _SOI_BEA_CROSS = os.path.join(_BEA_DIR, 'soi_bea_industry_codes.csv')
    paths['_BEA_INV'] = _BEA_INV = os.path.join(_BEA_DIR, 'NIPA_5.8.5B.xls')
    paths['_BEA_RES'] = _BEA_RES = os.path.join(_BEA_DIR, 'BEA_StdFixedAsset_Table5.1.xls')
    paths['_LAND_PATH'] = _LAND_PATH = os.path.join(_FIN_ACCT_DIR, '')
    paths['_B101_PATH'] = _B101_PATH = os.path.join(_FIN_ACCT_DIR, 'b101.csv')
    paths['_ECON_DEPR_IN_PATH'] = _ECON_DEPR_IN_PATH = os.path.join(_DEPR_DIR, 'Economic Depreciation Rates.csv')
    paths['_TAX_DEPR'] = _TAX_DEPR = os.path.join(_DEPR_DIR, 'tax_depreciation_rates.csv')
    paths['_SOI_DIR'] = _SOI_DIR = os.path.join(_RAW_DIR, 'soi')
    paths['_CORP_DIR'] = _CORP_DIR = os.path.join(_SOI_DIR, 'soi_corporate')
    paths['_TOT_CORP_IN_PATH'] = F_TOT_CORP_IN_PATH = os.path.join(_CORP_DIR, '2013sb1.csv')
    paths['_S_CORP_IN_PATH'] = _S_CORP_IN_PATH = os.path.join(_CORP_DIR, '2013sb3.csv')
    paths['_PRT_DIR'] = _PRT_DIR = os.path.join(_SOI_DIR, 'soi_partner')
    paths['_DETAIL_PART_CROSS_PATH'] = _DETAIL_PART_CROSS_PATH = os.path.join(_PRT_DIR, 'partner_crosswalk_detailed_industries.csv')
    paths['_INC_FILE'] = _INC_FILE = os.path.join(_PRT_DIR, '13pa01.xls')
    paths['_AST_FILE'] = _AST_FILE = os.path.join(_PRT_DIR, '13pa03.xls')
    #paths['_AST_profit_FILE'] = _AST_profit_FILE = os.path.join(_PRT_DIR, '12pa03_profit.xlsx')
    paths['_TYP_IN_CROSS_PATH'] = _TYP_IN_CROSS_PATH = os.path.join(_PRT_DIR, '13pa05_Crosswalk.csv')
    paths['_TYP_FILE'] = _TYP_FILE = os.path.join(_PRT_DIR, '13pa05.xls')
    paths['_PROP_DIR'] = _PROP_DIR = os.path.join(_SOI_DIR, 'soi_proprietorship')
    paths['_PRT_DIR'] = _PRT_DIR = os.path.join(_SOI_DIR, 'soi_partner')
    paths['_NFARM_PATH'] = _NFARM_PATH = os.path.join(_PROP_DIR, '13sp01br.xls')
    paths['_NFARM_INV'] = _NFARM_INV = os.path.join(_PROP_DIR, '13sp02is.xls')
    paths['_FARM_IN_PATH'] = _FARM_IN_PATH = os.path.join(_PROP_DIR, 'farm_data.csv')
    paths['_DETAIL_SOLE_PROP_CROSS_PATH'] = _DETAIL_SOLE_PROP_CROSS_PATH = os.path.join(_PROP_DIR, 'detail_sole_prop_crosswalk.csv')
    paths['_SOI_CODES'] = _SOI_CODES = os.path.join(_SOI_DIR, 'SOI_codes.csv')
    return paths


def str_modified(i):
    if i == 27.5:
        str_i = '27_5'
    else:
        str_i = str(int(i))
    return str_i


def diff_two_tables(df1, df2):
    assert tuple(df1.columns) == tuple(df2.columns)
    diffs = OrderedDict()
    for c in df1.columns:
        example = getattr(df1, c).iloc[0]
        can_diff = isinstance(example, numbers.Number)
        if can_diff:
            diffs[c] = getattr(df1, c) - getattr(df2, c)
        else:
            diffs[c] = getattr(df1, c)
    return pd.DataFrame(diffs)


def filter_user_params_for_econ(**user_params):
    return {k: v for k, v in user_params.items()
            if k.startswith('btax_econ_')}
