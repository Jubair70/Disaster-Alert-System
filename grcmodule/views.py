from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db.models import Count, Q
from django.http import (
    HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound,
    HttpResponseBadRequest, HttpResponse)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from datetime import date, timedelta
# from django.utils import simplejson
import json
import logging
import sys
import operator
import pandas as pds
from django.shortcuts import render
import numpy
import time
import datetime
from django.core.files.storage import FileSystemStorage

from django.core.urlresolvers import reverse


from django.db import (IntegrityError, transaction)
from django.db.models import ProtectedError
from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
# Menu imports
from usermodule.forms import MenuForm
from usermodule.models import MenuItem
# Organization Roles Import
from usermodule.models import OrganizationRole, MenuRoleMap, UserRoleMap
from django.forms.models import inlineformset_factory, modelformset_factory
from django.forms.formsets import formset_factory

from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from collections import OrderedDict
from django.template.loader import render_to_string
import os
from usermodule.views import error_page
import decimal




def __db_fetch_single_value(query):
    """
        function __db_fetch_single_value
        execute query and returns a single row's value a specific column
        Args:
            query: query to be executed
            dbname: intended database for this operation

        Returns:
            return text/numeric/null
    """
    cursor = connection.cursor()
    cursor.execute(query)
    fetchVal = cursor.fetchone()
    cursor.close()
    return fetchVal[0]


def __db_fetch_values_dict(query):
    """
            Function __db_fetch_values_dict return data as dictionary from select queries
            where key are corresponding column names
            Args:
                query: the query to be executed
                dbname: intended database for this operation

            Returns:
                select query return data as dictionary
    """
    cursor = connection.cursor()
    cursor.execute(query)
    fetchVal = dictfetchall(cursor)
    cursor.close()
    return fetchVal


def __db_commit_query(query):
    """
        function __db_commit_query executes the query in intended database
        Args:
            query: query to be executed
            dbname: intended database for this operation

        Returns:
            Nothing
    """
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()


def dictfetchall(cursor):
    """
    :param cursor:
    :return: dictionary values of the dictionary
    """
    desc = cursor.description
    return [
        OrderedDict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()]


def decimal_date_default(obj):
    """
    :param obj: string of datetime fields
    :return: converted datetime to decimal/isoformat when json.dumps()
    """
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return obj


@login_required
def index(request):
    """
    :param request:
    :return: test purpose whether the application is running or not
    """
    return render(request, "grcmodule/index.html")

@login_required
def upload_forecast_data_list(request):
    """
    :param request:
    :return: forecast data list
    """
    return render(request, 'grcmodule/upload_forecast_data_list.html')

@csrf_exempt
def get_upload_forecast_data_list(request):
    """
    :param request: ajax call for forecast data
    :return:  filtered data according to from and to date
    """
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    user_id = request.user.id
    query = """ select id,file_loc,file_name,file_source,to_char(added_on,'DD/MM/YYYY HH24:MI:SS')
                added_on,(select first_name || ' ' || last_name from auth_user where id = added_by::int) added_by,
                status::int status from flood_forecast_files fff
                where added_on::date between  '"""+str(from_date)+"""' and '"""+str(to_date)+"""'
             """
    data = json.dumps(__db_fetch_values_dict(query), default=decimal_date_default)
    return HttpResponse(data)


@login_required
@csrf_exempt
def upload_forecast_files_form(request):
    """
    :param request for forecast files
    :function: uploaded file in /home/vagrant out side application
    :return: if request is post then insert data else return blank form
    """
    if request.POST:
        file_name = request.POST.get('file_name')
        file_source = request.POST.get('file_source')
        forecast_date = request.POST.get('forecast_date')
        fd_new = datetime.datetime.strptime(forecast_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        forecast_date = fd_new
        added_by = request.user.id
        uploaded_file_path = ""
        if 'uploaded_file' in request.FILES:
            myfile = request.FILES['uploaded_file']
            forecast_file = request.FILES['uploaded_file']
            url = "/home/vagrant/GRC_DATA/FFWC/New/"
            userName = request.user
            fs = FileSystemStorage(location=url)
            if ".xlsx" in myfile.name:
                ext = ".xlsx"
            elif ".xls" in myfile.name:
                ext = ".xls"
            else:
                ext = ".csv"
            new_file_name = 'Bahadurabad Forecast (' + str(fd_new) + ')'+ext
            uploaded_file_path = url + new_file_name
            if fs.exists(new_file_name):
                fs.delete(new_file_name)
            filename = fs.save(new_file_name, myfile)

            insert_qry = """insert into flood_forecast_files(file_name,file_loc,file_source,
                            forecast_date,added_on,added_by)values('""" + str(file_name) + """',
                            '""" + str(uploaded_file_path) + """','""" + str(file_source) + """'
                            ,'""" + str(forecast_date) + """',now(),""" + str(added_by) + """)"""
            __db_commit_query(insert_qry)

            # forecast_data_insert(forecast_file_id, url+filename)
        # messages.success(request, '<i class="fa fa-check-circle"></i> New File has been uploaded successfully!',extra_tags='alert-success crop-both-side')
        return HttpResponseRedirect('/modules/upload-forecast-data/')
    file_src_qry = """ select file_source from flood_forecast_files_sources """
    df = pds.read_sql(file_src_qry, connection)
    file_src_list = df.file_source.tolist()
    return render(request, 'grcmodule/upload_forecast_files_form.html', {'file_src_list': file_src_list})


def forecast_data_insert(forecast_file_id, forecast_file):
    """
    :param forecast_file_id:
    :param forecast_file:
    :function: insert into flood_forecast_data if the celery is not available. not used in current system flow
    :return: nothing
    """
    try:
        df = pds.read_csv(forecast_file)
    except:
        df = pds.read_excel(forecast_file)
    flood_watch = df.columns[0]
    forecast_water_level = df.columns[1]
    observed_water_level = df.columns[2]
    for ix,r in df.iterrows():
        print(df[flood_watch][ix])
        if df[flood_watch][ix] == "YYYY-MM-DD HH:MM:SS":
            continue
        fld_wtch = df[flood_watch][ix]
        frcst_wtr_lvl = df[forecast_water_level][ix]
        observed_wtr_lvl = df[observed_water_level][ix]
        ins_qry = """ INSERT INTO public.flood_forecast_data (forecast_file_id, flood_watch, forecast_water_level, observed_water_level) VALUES("""+str(forecast_file_id)+""", '"""+str(fld_wtch)+"""', case when '"""+str(frcst_wtr_lvl)+"""' = '-9999' then null else '"""+str(frcst_wtr_lvl)+"""' end , case when '"""+str(observed_wtr_lvl)+"""' = '-9999' then null else '"""+str(observed_wtr_lvl)+"""' end) """
        __db_commit_query(ins_qry)
        print(ix,df[flood_watch][ix],df[forecast_water_level][ix],df[observed_water_level][ix])



@login_required
@csrf_exempt
def delete_forecast_files(request,file_id):
    """
    :param request:
    :param file_id:
    :function : delete data from tables flood_forecast_files and flood_forecast_data
    :return: deleted list of forecast data
    """
    qry = """ select substring(file_loc from 2) file_loc from flood_forecast_files where id = """+str(file_id)
    df = pds.read_sql(qry,connection)
    if not df.empty:
        path = df.file_loc.tolist()[0]
        os.remove(path)
    qry = """ delete from flood_forecast_data where forecast_file_id = """ + str(file_id)
    __db_commit_query(qry)

    qry = """ delete from flood_forecast_files where id = """ + str(file_id)
    __db_commit_query(qry)
    return HttpResponseRedirect('/modules/upload-forecast-data/')

@login_required
def flood_index_files_list(request):
    """
    :param request:
    :return: flood index list
    """
    return render(request, 'grcmodule/flood_index_files_list.html')

@csrf_exempt
def get_flood_index_files_list(request):
    """
    :param request:
    :return: filtered index files list. currently no filter is used
    """
    # from_date = request.POST.get('from_date')
    # to_date = request.POST.get('to_date')
    query = """ select id,file_loc,published_year,file_name,file_source,to_char(added_on,'DD/MM/YYYY HH:MI:SS') added_on,(select first_name || ' ' || last_name from auth_user where id = added_by::int) added_by from flood_index_files fff """
    print(query)
    data = json.dumps(__db_fetch_values_dict(query), default=decimal_date_default)
    return HttpResponse(data)

@login_required
@csrf_exempt
def flood_index_files_form(request):
    """
        :param request
        :function: insert into flood_index_files
        :return: if request is post then insert into flood_index_files else index form
    """
    if request.POST:
        file_name = request.POST.get('file_name')
        file_source = request.POST.get('file_source')
        published_year = request.POST.get('published_year')
        added_by = request.user.id
        uploaded_file_path = ""
        if 'uploaded_file' in request.FILES:
            myfile = request.FILES['uploaded_file']
            forecast_file = request.FILES['uploaded_file']
            print(forecast_file)
            url = "static/media/uploaded_files/"
            userName = request.user
            fs = FileSystemStorage(location=url)
            # myfile.name = str(datetime.datetime.now().date()) + "_" + str(userName) + "_" + str(myfile.name)
            if ".xlsx" in myfile.name:
                myfile.name = file_name+"_"+file_source+"_"+published_year+".xlsx"
            elif ".xls" in myfile.name:
                myfile.name = file_name+"_"+file_source+"_"+published_year+".xls"
            else:
                myfile.name = file_name + "_" + file_source + "_" + published_year + ".csv"
            filename = fs.save(myfile.name, myfile)
            uploaded_file_path = "/"+url+ myfile.name

            insert_qry = """ insert into flood_index_files(file_name,file_loc,file_source,published_year,added_on,added_by) values('"""+str(file_name)+"""','"""+str(uploaded_file_path)+"""','"""+str(file_source)+"""','"""+str(published_year)+"""',now(),"""+str(added_by)+""") returning id"""
            print(insert_qry)
            index_file_id = __db_fetch_single_value(insert_qry)
            index_data_insert(index_file_id, url+filename)
        # messages.success(request, '<i class="fa fa-check-circle"></i> New File has been uploaded successfully!',extra_tags='alert-success crop-both-side')
        return HttpResponseRedirect('/modules/flood-index-files/')
    return render(request,'grcmodule/flood_index_files_form.html')

def index_data_insert(index_file_id, index_file):
    """
    :param index_file_id:
    :param index_file:
    :function insert index file data into  flood_geo_data, flood_hh_structure, flood_population_data
    :return: nothing
    """
    try:
        df = pds.read_csv(index_file)
    except:
        df = pds.read_excel(index_file)
    clm_union_code = 'Union_Code'
    clm_div_name = 'DIV_NAME'
    clm_dist_name = 'DIST_NAME'
    clm_upz_name = 'UPAZILA_NAME'
    clm_union_name = 'UNI_NAME'
    clm_category_label = 'Category'
    clm_total_area = 'AREA'
    clm_ultra_poor = 'poverty_U'
    clm_average_flood_level = 'Avarage_FL'
    clm_pucca = 'Pucca'
    clm_s_pucca = 'S_pucca'
    clm_kutcha = 'Kutcha'
    clm_jhupri = 'Jhupri'
    clm_all_ages = 'ALL_AGES'
    clm_h0_4 = 'H0_4'
    clm_h5_9 = 'H5_9'
    clm_h10_14 = 'H10_14'
    clm_h15_19 = 'H15_19'
    clm_h20_24 = 'H20_24'
    clm_h25_29 = 'H25_29'
    clm_h30_49 = 'H30_49'
    clm_h50_59 = 'H50_59'
    clm_h60_64 = 'H60_64'
    clm_h65 = 'H65'
    category_dict = {
        'Char land': 1,
        'Outside embankment':2,
        'Protected/ Far away': 3
    }

    for ix,r in df.iterrows():
        union_code  = df[clm_union_code][ix]
        div_code    = str(df[clm_union_code][ix])[0:2]
        dist_code   = str(df[clm_union_code][ix])[0:4]
        upz_code    = str(df[clm_union_code][ix])[0:6]
        div_name    = df[clm_div_name][ix]
        dist_name = str(df[clm_dist_name][ix]).replace('\'', '\'\'')
        upz_name = str(df[clm_upz_name][ix]).replace('\'', '\'\'')
        union_name = str(df[clm_union_name][ix]).replace('\'', '\'\'')
        category_label = df[clm_category_label][ix]
        category    = category_dict[category_label]
        total_area  = df[clm_total_area][ix]
        ultra_poor  = df[clm_ultra_poor][ix]
        average_flood_level = df[clm_average_flood_level][ix]
        ins_qry_flood_geo_data =  """ INSERT INTO public.flood_geo_data
                    (div_code, div_name, dist_code, dist_name, upz_code, upz_name
                    , union_code, union_name, category, category_label, total_area
                    , ultra_poor, average_flood_level,index_file_id)
                    VALUES('""" + str(div_code) + """', '""" + str(div_name) + """', '""" + str(dist_code) + """', '""" + str(dist_name) + """', '""" + str(upz_code) + """', '""" + str(upz_name) + """'
                    , '""" + str(union_code) + """', '""" + str(union_name) + """', """ + str(category) + """, '""" + str(category_label) + """', """ + str(total_area) + """
                    , """ + str(ultra_poor) + """, """ + str(average_flood_level) + """, """ + str(index_file_id) + """)
                    """
        __db_commit_query(ins_qry_flood_geo_data)

        pucca   = df[clm_pucca][ix]
        s_pucca = df[clm_s_pucca][ix]
        kutcha  = df[clm_kutcha][ix]
        jhupri  = df[clm_jhupri][ix]

        ins_qry_flood_hh_structure = """ INSERT INTO public.flood_hh_structure
                            (union_code, pucca, s_pucca, kutcha, jhupri,index_file_id)
                            VALUES('""" + str(union_code) + """','""" + str(pucca) + """', """ + str(s_pucca) + """, """ + str(kutcha) + """, """ + str(jhupri) + """, """ + str(index_file_id) + """)
                            """
        __db_commit_query(ins_qry_flood_hh_structure)

        all_ages = df[clm_all_ages][ix]
        h0_4    = df[clm_h0_4][ix]
        h5_9    = df[clm_h5_9][ix]
        h10_14  = df[clm_h10_14][ix]
        h15_19  = df[clm_h15_19][ix]
        h20_24  = df[clm_h20_24][ix]
        h25_29  = df[clm_h25_29][ix]
        h30_49  = df[clm_h30_49][ix]
        h50_59  = df[clm_h50_59][ix]
        h60_64  = df[clm_h60_64][ix]
        h65     = df[clm_h65][ix]

        ins_qry_flood_population_data =  """ INSERT INTO public.flood_population_data
                    (union_code, all_ages, h0_4, h5_9
                    , h10_14, h15_19, h20_24, h25_29
                    , h30_49, h50_59, h60_64, h65,index_file_id)
                    VALUES('""" + str(union_code) + """', """ + str(all_ages) + """, """ + str(h0_4) + """, """ + str(h5_9) + """
                    , """ + str(h10_14) + """, """ + str(h15_19) + """, """ + str(h20_24) + """, """ + str(h25_29) + """
                    , """ + str(h30_49) + """, """ + str(h50_59) + """, """ + str(h60_64) + """, """ + str(h65) + """, """ + str(index_file_id) + """)
                    """
        __db_commit_query(ins_qry_flood_population_data)


@login_required
@csrf_exempt
def delete_index_files(request,file_id):
    """
    :param request:
    :param file_id:
    :function delete data from flood_index_files, flood_hh_structure, flood_population_data, flood_geo_data
    :return: deleted list of index files
    """
    qry = """ select substring(file_loc from 2) file_loc from flood_index_files where id = """+str(file_id)
    df = pds.read_sql(qry,connection)
    if not df.empty:
        path = df.file_loc.tolist()[0]
        os.remove(path)
    qry = """ delete from flood_index_files where id = """ + str(file_id)
    __db_commit_query(qry)

    qry = """ delete from flood_hh_structure where index_file_id = """ + str(file_id)
    __db_commit_query(qry)

    qry = """ delete from flood_population_data where index_file_id = """ + str(file_id)
    __db_commit_query(qry)

    qry = """ delete from flood_geo_data where index_file_id = """ + str(file_id)
    __db_commit_query(qry)
    return HttpResponseRedirect('/modules/flood-index-files/')


@login_required
@csrf_exempt
def flood_index_weightage_parameters_form(request):
    """
        :param request
        :function: insert into flood_index_weightage_parameters
        :return: if request is post then insert into flood_index_weightage_parameters else flood_index_weightage_parameters form
    """
    if request.POST:
        pucca = request.POST.get('pucca')
        s_pucca = request.POST.get('s_pucca')
        kutcha = request.POST.get('kutcha')
        jhupri = request.POST.get('jhupri')
        hh_structure = request.POST.get('hh_structure')
        dp_population = request.POST.get('dp_population')
        low_area = request.POST.get('low_area')
        ultra_poor = request.POST.get('ultra_poor')
        updt_tbl_qry = """ UPDATE public.flood_index_weightage_parameters SET pucca="""+str(pucca)+""", s_pucca="""+str(s_pucca)+""", kutcha="""+str(kutcha)+""", jhupri="""+str(jhupri)+""", hh_structure="""+str(hh_structure)+""", dp_population="""+str(dp_population)+""", low_area="""+str(low_area)+""", ultra_poor="""+str(ultra_poor)+""" WHERE id=  1 """
        __db_commit_query(updt_tbl_qry)
        return HttpResponseRedirect('/modules/flood-index-files/')
    qry = """ select * from  flood_index_weightage_parameters limit 1 """
    df = pds.read_sql(qry,connection)
    if not df.empty:
        pucca  = df.pucca.tolist()[0]
        s_pucca = df.s_pucca.tolist()[0]
        kutcha = df.kutcha.tolist()[0]
        jhupri = df.jhupri.tolist()[0]
        hh_structure = df.hh_structure.tolist()[0]
        dp_population = df.dp_population.tolist()[0]
        low_area = df.low_area.tolist()[0]
        ultra_poor = df.ultra_poor.tolist()[0]
        return render(request,'grcmodule/flood_index_weightage_parameters_form.html',{
            'pucca':pucca,
            's_pucca':s_pucca,
            'kutcha':kutcha,
            'jhupri':jhupri,
            'hh_structure':hh_structure,
            'dp_population':dp_population,
            'low_area':low_area,
            'ultra_poor':ultra_poor
        })

    return render(request,'grcmodule/flood_index_weightage_parameters_form.html')


@login_required
def dashboard(request):
    """
    :param request:
    :return: dashboard
    """
    return render(request,'grcmodule/dashboard.html')

@csrf_exempt
def get_dashboard_data(request):
    """
    :param request:
    :function dashboard data using ajax
    :return: datetime wise forecast data from table and  date wise graph data for graph
    """
    tbl_qry = """ select (select file_source from flood_forecast_files where id = ffd.forecast_file_id ),to_char(flood_watch,'YYYY-MM-DD HH:MI:SS') flood_watch,coalesce(forecast_water_level,'0') forecast_water_level from flood_forecast_data ffd order by flood_watch """
    tbl_data = __db_fetch_values_dict(tbl_qry)

    # for which page to show
    qry = """ select ("""+str(len(tbl_data))+"""-count(*))/10  page_num from flood_forecast_data where flood_watch::date >= (select flood_watch from (select distinct flood_watch::date from flood_forecast_data ffd order by flood_watch desc limit 6) as ints order by flood_watch::date limit 1) """
    print(qry)
    df = pds.read_sql(qry,connection)
    print(df)
    if not df.empty:
        page_num = df.page_num.tolist()[0]
    else:
        page_num = 0

    grph_qry = """ select to_char(flood_watch::date,'YYYY-MM-DD') flood_watch,coalesce(avg(forecast_water_level::float8),0) forecast_water_level from flood_forecast_data ffd group by flood_watch::date order by flood_watch::date """
    df = pds.read_sql(grph_qry,connection)
    flood_watch = df.flood_watch.tolist()
    forecast_water_level = df.forecast_water_level.tolist()
    data = json.dumps({
                        'page_num':page_num,
                        'tbl_data':tbl_data,
                        'flood_watch':flood_watch,
                        'forecast_water_level':forecast_water_level
                      })
    return HttpResponse(data)


@login_required
def eap_analysis(request):
    """
    :param request:
    :return: flood eap analysis report
    """
    qry = """ select file_source from flood_index_files cif order by published_year desc limit 1 """
    df = pds.read_sql(qry,connection)
    file_source = df.file_source.tolist()[0]
    return render(request,'grcmodule/eap_analysis.html',{'file_source': file_source})

@csrf_exempt
def flood_depth_data(request):
    """
    :param request:
    :return: table and map data with current flood depth and peak flood depth
    """
    qry = """ 
            with t as (
            select union_code, watchtime, flood_depth as current_flood_depth,normalized_impact as impact ,round(vulnaribity_index::numeric,2)::text vulnaribity_index,round(potential_damage::numeric,2)::text potential_damage,potential_damage_rank	 from flood_data_current fdc where watchtime::date = (select distinct watchtime::date from flood_data_current order by watchtime limit 1) 
            ), t1 as (
            select union_code, watchtime, flood_depth as peak_flood_depth from flood_data_current fdc where watchtime::date >= (select distinct watchtime::date from flood_data_current order by watchtime desc limit 1) 
            ), sht as (
            select t.union_code, t.watchtime as current_day,current_flood_depth, t1.watchtime as peak_day,case when peak_flood_depth is null then current_flood_depth else peak_flood_depth end peak_flood_depth from t left join t1 on t.union_code = t1.union_code
            )select fgd.*,sht.* from flood_geo_data fgd left join sht on fgd.union_code  = sht.union_code where fgd.index_file_id  = (select id from flood_index_files fif order by published_year desc limit 1 )
            """
    df = pds.read_sql(qry, connection)
    df['current_day'] = df['current_day'].astype(str)
    df['peak_day'] = df['peak_day'].astype(str)
    df = df.to_dict(orient='records')

    df_obj = {}
    df_obj_peak = {}
    var_list = []
    flood_peak_list = []

    # depth map
    for x in df:
        df_obj[x["union_code"]] = float(x["current_flood_depth"]) \
            if x["current_flood_depth"] is not None else 0
        var_list.append(float(x["current_flood_depth"])) \
            if x["current_flood_depth"] is not None else 0
        df_obj_peak[x["union_code"]] = float(x["peak_flood_depth"]) \
            if x["peak_flood_depth"] is not None else 0
        flood_peak_list.append(float(x["peak_flood_depth"])) \
            if x["peak_flood_depth"] is not None else 0

    curr_date = ''
    peak_date = ''
    if len(df):
        curr_date = df[0]['current_day']
        peak_date = df[0]['peak_day']

    data = json.dumps({
        'df': df,
        'df_obj': df_obj,
        'df_obj_peak': df_obj_peak,
        'var_list': var_list,
        'flood_peak_list': flood_peak_list,
        'curr_date': curr_date,
        'peak_date': peak_date
    })
    return HttpResponse(data)


@csrf_exempt
def flood_impact_data(request):
    """
    :param request:
    :return: table and map data with peak flood depth and impact
    """
    qry = """ 
            with t as (
            select union_code,watchtime,flood_depth as current_flood_depth,normalized_impact as impact ,round(vulnaribity_index::numeric,2)::text vulnaribity_index,round(potential_damage::numeric,2)::text potential_damage,potential_damage_rank	 from flood_data_current fdc where watchtime::date = (select distinct watchtime::date from flood_data_current order by watchtime limit 1) 
            ), t1 as (
            select union_code,watchtime,flood_depth as peak_flood_depth from flood_data_current fdc where watchtime::date >= (select distinct watchtime::date from flood_data_current order by watchtime desc limit 1) 
            ), sht as (
            select t.union_code,t.watchtime as current_day,current_flood_depth,t1.watchtime as peak_day,case when peak_flood_depth is null then current_flood_depth else peak_flood_depth end peak_flood_depth,round(impact::numeric,2)::text impact  from t left join t1 on t.union_code = t1.union_code
            )select fgd.*,sht.* from flood_geo_data fgd left join sht on fgd.union_code  = sht.union_code where impact::float > 0.25 and  fgd.index_file_id  = (select id from flood_index_files fif order by published_year desc limit 1 )
           """
    df = pds.read_sql(qry, connection)
    df['current_day'] = df['current_day'].astype(str)
    df['peak_day'] = df['peak_day'].astype(str)
    df = df.to_dict(orient='records')

    qry = """
        with t as (
            select union_code,watchtime,flood_depth as current_flood_depth,impact,normalized_impact ,round(vulnaribity_index::numeric,2)::text vulnaribity_index,round(potential_damage::numeric,2)::text potential_damage,potential_damage_rank	 from flood_data_current fdc where watchtime::date = (select distinct watchtime::date from flood_data_current order by watchtime limit 1) 
            ), t1 as (
            select union_code,watchtime,flood_depth as peak_flood_depth from flood_data_current fdc where watchtime::date >= (select distinct watchtime::date from flood_data_current order by watchtime desc limit 1) 
            ), sht as (
            select t.union_code,t.watchtime as current_day,current_flood_depth,t1.watchtime as peak_day,case when peak_flood_depth is null then current_flood_depth else peak_flood_depth end peak_flood_depth,case when normalized_impact::float >= 0 and normalized_impact::float < 0.25 then round(impact::numeric,2)::text else round(normalized_impact::numeric,2)::text  end  impact  from t left join t1 on t.union_code = t1.union_code
            )select fgd.*,sht.* from flood_geo_data fgd left join sht on fgd.union_code  = sht.union_code where fgd.index_file_id  = (select id from flood_index_files fif order by published_year desc limit 1 )
        """
    df_map = pds.read_sql(qry, connection)
    df_map = df_map.to_dict(orient='records')
    df_impact = {}
    impact_list = []

    # impact map
    for y in df_map:
        df_impact[y["union_code"]] = float(y["impact"]) \
            if y["impact"] is not None else 0
        impact_list.append(float(y["impact"])) \
            if y["impact"] is not None else 0

    curr_date = ''
    peak_date = ''
    if len(df):
        curr_date = df[0]['current_day']
        peak_date = df[0]['peak_day']

    data = json.dumps({
        'df': df,
        'df_impact': df_impact,
        'impact_list': impact_list,
        'curr_date': curr_date,
        'peak_date': peak_date
    })
    return HttpResponse(data)


@csrf_exempt
def flood_potential_data(request):
    """
    :param request:
    :return: table and map data with peak flood depth, impact , vulnerability_index, potential_damage, potential_damage_rank
    """
    qry = """ 
             with t as (
             select union_code,watchtime,flood_depth as current_flood_depth,normalized_impact as impact ,round(vulnaribity_index::numeric,2)::text vulnaribity_index,round(potential_damage::numeric,2)::text potential_damage,potential_damage_rank	 from flood_data_current fdc where watchtime::date = (select distinct watchtime::date from flood_data_current order by watchtime limit 1)
             ), t1 as (
             select union_code,watchtime,flood_depth as peak_flood_depth from flood_data_current fdc where watchtime::date >= (select distinct watchtime::date from flood_data_current order by watchtime desc limit 1)
             ), sht as (
             select t.union_code,t.watchtime as current_day,current_flood_depth,t1.watchtime as peak_day,case when peak_flood_depth is null then current_flood_depth else peak_flood_depth end peak_flood_depth, round(impact::numeric,2)::text impact ,vulnaribity_index,potential_damage,potential_damage_rank  from t left join t1 on t.union_code = t1.union_code
             )select fgd.*,sht.* from flood_geo_data fgd left join sht on fgd.union_code  = sht.union_code where impact::float > 0.25 and fgd.index_file_id  = (select id from flood_index_files fif order by published_year desc limit 1 )
               """
    df = pds.read_sql(qry, connection)
    df['current_day'] = df['current_day'].astype(str)
    df['peak_day'] = df['peak_day'].astype(str)
    df = df.to_dict(orient='records')

    df_potential = {}
    potential_list = []
    df_rank = {}
    df_impact = {}

    # potential map
    for y in df:
        df_potential[y["union_code"]] = float(y["potential_damage"]) \
            if y["potential_damage"] is not None else 0
        df_rank[y["union_code"]] = float(y["potential_damage_rank"]) \
            if y["potential_damage_rank"] is not None else 0
        df_impact[y["union_code"]] = float(y["impact"]) \
            if y["impact"] is not None else 0
        potential_list.append(float(y["potential_damage"])) \
            if y["potential_damage"] is not None else 0

    curr_date = ''
    peak_date = ''
    if len(df):
        curr_date = df[0]['current_day']
        peak_date = df[0]['peak_day']

    data = json.dumps({
        'df': df,
        'df_potential': df_potential,
        'df_rank': df_rank,
        'df_impact': df_impact,
        'potential_list': potential_list,
        'curr_date': curr_date,
        'peak_date': peak_date
    })
    return HttpResponse(data)


@login_required
def cyclone_index_files_list(request):
    """
    :param request:
    :return: cyclone index file list
    """
    return render(request, 'grcmodule/cyclone_index_files_list.html')

@csrf_exempt
def get_cyclone_index_files_list(request):
    """
    :param request:
    :return: filtered cyclone index files list. currently no filter is used
    """
    # from_date = request.POST.get('from_date')
    # to_date = request.POST.get('to_date')
    query = """ select id,file_loc,published_year,file_name,file_source,to_char(added_on,'DD/MM/YYYY HH:MI:SS') added_on,(select first_name || ' ' || last_name from auth_user where id = added_by::int) added_by from cyclone_index_files fff """
    print(query)
    data = json.dumps(__db_fetch_values_dict(query), default=decimal_date_default)
    return HttpResponse(data)


@login_required
@csrf_exempt
def cyclone_index_files_form(request):
    """
        :param request
        :function: insert into cyclone_index_files
        :return: if request is post then insert into flood_index_files else index form
    """
    if request.POST:
        file_name = request.POST.get('file_name')
        file_source = request.POST.get('file_source')
        published_year = request.POST.get('published_year')
        added_by = request.user.id
        uploaded_file_path = ""
        if 'uploaded_file' in request.FILES:
            myfile = request.FILES['uploaded_file']
            forecast_file = request.FILES['uploaded_file']
            print(forecast_file)
            url = "static/media/uploaded_files/"
            userName = request.user
            fs = FileSystemStorage(location=url)
            # myfile.name = str(datetime.datetime.now().date()) + "_" + str(userName) + "_" + str(myfile.name)
            if ".xlsx" in myfile.name:
                myfile.name = file_name+"_"+file_source+"_"+published_year+".xlsx"
            elif ".xls" in myfile.name:
                myfile.name = file_name+"_"+file_source+"_"+published_year+".xls"
            else:
                myfile.name = file_name + "_" + file_source + "_" + published_year + ".csv"
            filename = fs.save(myfile.name, myfile)
            uploaded_file_path = "/"+url+ myfile.name

            insert_qry = """ insert into cyclone_index_files(file_name,file_loc,file_source,published_year,added_on,added_by) values('"""+str(file_name)+"""','"""+str(uploaded_file_path)+"""','"""+str(file_source)+"""','"""+str(published_year)+"""',now(),"""+str(added_by)+""") returning id"""
            print(insert_qry)
            index_file_id = __db_fetch_single_value(insert_qry)
            cyclone_index_data_insert(index_file_id, url+filename)
        # messages.success(request, '<i class="fa fa-check-circle"></i> New File has been uploaded successfully!',extra_tags='alert-success crop-both-side')
        return HttpResponseRedirect('/modules/cyclone-index-files/')
    return render(request,'grcmodule/cyclone_index_files_form.html')

def cyclone_index_data_insert(index_file_id, index_file):
    """
        :param index_file_id:
        :param index_file:
        :function insert index file data into  cyclone_geo_data, cyclone_hh_structure, cyclone_population_data
        :return: nothing
    """
    try:
        df = pds.read_csv(index_file)
    except:
        df = pds.read_excel(index_file)
    clm_union_code = df.columns[1]
    clm_div_name = df.columns[2]
    clm_dist_name = df.columns[3]
    clm_upz_name = df.columns[4]
    clm_psa_name = df.columns[5]
    clm_union_name = df.columns[6]
    clm_zone_label = df.columns[7]
    clm_ultra_poor = df.columns[41]
    clm_shelter_capacity = df.columns[43]
    clm_cpp_volunteer = df.columns[36]
    clm_upazila_population = df.columns[37]
    clm_pucca = df.columns[34]
    clm_s_pucca = df.columns[33]
    clm_kutcha = df.columns[32]
    clm_jhupri = df.columns[31]
    clm_all_ages = df.columns[8]
    clm_h0_4 = df.columns[9]
    clm_h5_9 = df.columns[11]
    clm_h10_14 = df.columns[13]
    clm_h15_19 = df.columns[15]
    clm_h20_24 = df.columns[17]
    clm_h25_29 = df.columns[19]
    clm_h30_49 = df.columns[21]
    clm_h50_59 = df.columns[23]
    clm_h60_64 = df.columns[25]
    clm_h65 = df.columns[27]
    zone_dict = {
        'Central Zone': 1,
        'Eastern Zone': 2,
        'Western Zone': 3
    }

    for ix,r in df.iterrows():
        union_code  = df[clm_union_code][ix]
        div_code    = str(df[clm_union_code][ix])[0:2]
        dist_code   = str(df[clm_union_code][ix])[0:4]
        upz_code    = str(df[clm_union_code][ix])[0:6]
        div_name    = df[clm_div_name][ix]
        dist_name   = str(df[clm_dist_name][ix]).replace('\'', '\'\'')
        upz_name    = str(df[clm_upz_name][ix]).replace('\'', '\'\'')
        union_name  = str(df[clm_union_name][ix]).replace('\'', '\'\'')
        zone_label = df[clm_zone_label][ix]
        zone_id    = zone_dict[zone_label]
        psa_name  = str(df[clm_psa_name][ix]).replace('\'', '\'\'')
        ultra_poor  = df[clm_ultra_poor][ix]
        shelter_capacity = df[clm_shelter_capacity][ix]
        cpp_volunteer = df[clm_cpp_volunteer][ix]
        upazila_population = df[clm_upazila_population][ix]
        """ + str() + """
        ins_qry_cyclone_geo_data =  """ 
            INSERT INTO public.cyclone_geo_data
            (div_code, div_name, dist_code, dist_name,
             upz_code, upz_name, union_code, union_name,
              zone_id, zone_label, cpp_volunteer, upazila_population,
               ultra_poor, shelter_capacity, index_file_id, psa_name)
            VALUES('""" + str(div_code) + """', '""" + str(div_name) + """', '""" + str(dist_code) + """', '""" + str(dist_name) + """',
             '""" + str(upz_code) + """', '""" + str(upz_name) + """', '""" + str(union_code) + """', '""" + str(union_name) + """',
              """ + str(zone_id) + """, '""" + str(zone_label) + """', """ + str(cpp_volunteer) + """, """ + str(upazila_population) + """, 
              """ + str(ultra_poor) + """, """ + str(shelter_capacity) + """, """ + str(index_file_id) + """, '""" + str(psa_name) + """');

                                    """

        __db_commit_query(ins_qry_cyclone_geo_data)

        pucca   = df[clm_pucca][ix]
        s_pucca = df[clm_s_pucca][ix]
        kutcha  = df[clm_kutcha][ix]
        jhupri  = df[clm_jhupri][ix]

        ins_qry_cyclone_hh_structure = """ 
        INSERT INTO public.cyclone_hh_structure
        (union_code, pucca, s_pucca, kutcha, jhupri, index_file_id)
        VALUES('""" + str(union_code) + """', """ + str(pucca) + """, """ + str(s_pucca) + """, """ + str(kutcha) + """, 
        """ + str(jhupri) + """, """ + str(index_file_id) + """);

                            """
        __db_commit_query(ins_qry_cyclone_hh_structure)

        all_ages = df[clm_all_ages][ix]
        h0_4    = df[clm_h0_4][ix]
        h5_9    = df[clm_h5_9][ix]
        h10_14  = df[clm_h10_14][ix]
        h15_19  = df[clm_h15_19][ix]
        h20_24  = df[clm_h20_24][ix]
        h25_29  = df[clm_h25_29][ix]
        h30_49  = df[clm_h30_49][ix]
        h50_59  = df[clm_h50_59][ix]
        h60_64  = df[clm_h60_64][ix]
        h65     = df[clm_h65][ix]

        ins_qry_cyclone_population_data =  """ 
        INSERT INTO public.cyclone_population_data
        (union_code, all_ages, h0_4, h5_9,
         h10_14, h15_19, h20_24, h25_29,
          h30_49, h50_59, h60_64, h65, index_file_id)
        VALUES('""" + str(union_code) + """', """ + str(all_ages) + """, """ + str(h0_4) + """, """ + str(h5_9) + """,
         """ + str(h10_14) + """, """ + str(h15_19) + """, """ + str(h20_24) + """, """ + str(h25_29) + """,
          """ + str(h30_49) + """, """ + str(h50_59) + """, """ + str(h60_64) + """, """ + str(h65) + """, """ + str(index_file_id) + """);
                    """
        __db_commit_query(ins_qry_cyclone_population_data)


@login_required
@csrf_exempt
def cyclone_index_weightage_parameters_form(request):
    """
            :param request
            :function: insert into cyclone_index_weightage_parameters
            :return: if request is post then insert into cyclone_index_weightage_parameters else return cyclone_index_weightage_parameters form
    """
    if request.POST:
        pucca = request.POST.get('pucca')
        s_pucca = request.POST.get('s_pucca')
        kutcha = request.POST.get('kutcha')
        jhupri = request.POST.get('jhupri')
        hh_structure = request.POST.get('hh_structure')
        dp_population = request.POST.get('dp_population')
        cpp_volunteer = request.POST.get('cpp_volunteer')
        ultra_poor = request.POST.get('ultra_poor')
        unserved_population = request.POST.get('unserved_population')
        updt_tbl_qry = """ UPDATE cyclone_index_weightage_parameters SET pucca="""+str(pucca)+""", s_pucca="""+str(s_pucca)+""", kutcha="""+str(kutcha)+""", jhupri="""+str(jhupri)+""", hh_structure="""+str(hh_structure)+""", dp_population="""+str(dp_population)+""", cpp_volunteer="""+str(cpp_volunteer)+""", ultra_poor="""+str(ultra_poor)+""", unserved_population = """+str(unserved_population)+""" WHERE id =  1 """
        __db_commit_query(updt_tbl_qry)
        return HttpResponseRedirect('/modules/cyclone-index-files/')
    qry = """ select * from  cyclone_index_weightage_parameters limit 1 """
    df = pds.read_sql(qry,connection)
    if not df.empty:
        pucca  = df.pucca.tolist()[0]
        s_pucca = df.s_pucca.tolist()[0]
        kutcha = df.kutcha.tolist()[0]
        jhupri = df.jhupri.tolist()[0]
        hh_structure = df.hh_structure.tolist()[0]
        dp_population = df.dp_population.tolist()[0]
        cpp_volunteer = df.cpp_volunteer.tolist()[0]
        ultra_poor = df.ultra_poor.tolist()[0]
        unserved_population = df.unserved_population.tolist()[0]
        return render(request,'grcmodule/cyclone_index_weightage_parameters_form.html',{
            'pucca':pucca,
            's_pucca':s_pucca,
            'kutcha':kutcha,
            'jhupri':jhupri,
            'hh_structure':hh_structure,
            'dp_population':dp_population,
            'cpp_volunteer':cpp_volunteer,
            'ultra_poor':ultra_poor,
            'unserved_population':unserved_population
        })

    return render(request,'grcmodule/cyclone_index_weightage_parameters_form.html')


@login_required
@csrf_exempt
def delete_cyclone_index_files(request,file_id):
    """
    :param request:
    :param file_id:
    :function delete from cyclone_hh_structure,cyclone_population_data,cyclone_geo_data
    :return: deleted cyclone index list
    """
    qry = """ select substring(file_loc from 2) file_loc from cyclone_index_files where id = """+str(file_id)
    df = pds.read_sql(qry,connection)
    if not df.empty:
        path = df.file_loc.tolist()[0]
        os.remove(path)
    qry = """ delete from cyclone_index_files where id = """ + str(file_id)
    __db_commit_query(qry)

    qry = """ delete from cyclone_hh_structure where index_file_id = """ + str(file_id)
    __db_commit_query(qry)

    qry = """ delete from cyclone_population_data where index_file_id = """ + str(file_id)
    __db_commit_query(qry)

    qry = """ delete from cyclone_geo_data where index_file_id = """ + str(file_id)
    __db_commit_query(qry)
    return HttpResponseRedirect('/modules/cyclone-index-files/')


@login_required
def upload_cyclone_forecast_data_list(request):
    """
    :param request:
    :return: cyclone forecast data
    """
    return render(request, 'grcmodule/upload_cyclone_forecast_data_list.html')

@csrf_exempt
def get_upload_cyclone_forecast_data_list(request):
    """
    :param request: from date and to date
    :return: return filtered data
    """
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    user_id = request.user.id
    query = """
         select id,file_loc,file_name,file_source,to_char(added_on,'DD/MM/YYYY HH24:MI:SS') added_on,
        (select first_name || ' ' || last_name from auth_user where id = added_by::int) added_by,status::int status
         from cyclone_forecast_files fff where added_on::date between  '"""+str(from_date)+"""' and '"""+str(to_date)+"""'
     """
    data = json.dumps(__db_fetch_values_dict(query), default=decimal_date_default)
    return HttpResponse(data)


@login_required
@csrf_exempt
def upload_cyclone_forecast_files_form(request):
    """
    :param request:
    :return: forecast form
    """
    if request.POST:
        file_name = request.POST.get('file_name')
        file_source = request.POST.get('file_source')
        forecast_date = request.POST.get('forecast_date')
        fd_new = datetime.datetime.strptime(forecast_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        forecast_date = fd_new
        added_by = request.user.id
        uploaded_file_path = ""
        if 'uploaded_file' in request.FILES:
            myfile = request.FILES['uploaded_file']
            forecast_file = request.FILES['uploaded_file']
            # print(forecast_file)
            url = "/home/vagrant/GRC_DATA/Cyclone/FFWC/New/"
            userName = request.user
            fs = FileSystemStorage(location=url)
            if ".xlsx" in myfile.name:
                ext = ".xlsx"
            elif ".xls" in myfile.name:
                ext = ".xls"
            else:
                ext = ".csv"
            new_file_name = 'Cyclone Forecast (' + str(fd_new) + ')'+ext
            uploaded_file_path = url + new_file_name
            if fs.exists(new_file_name):
                fs.delete(new_file_name)
            filename = fs.save(new_file_name, myfile)
            insert_qry = """
                insert into cyclone_forecast_files(file_name,file_loc,file_source,forecast_date,added_on,added_by)
                values('""" + str(file_name) + """','""" + str(uploaded_file_path) + """'
                ,'""" + str(file_source) + """','""" + str(forecast_date) + """',now(),""" + str(added_by) + """)
                """
            __db_commit_query(insert_qry)
        # messages.success(request, '<i class="fa fa-check-circle"></i>
        # New File has been uploaded successfully!',extra_tags='alert-success crop-both-side')
        return HttpResponseRedirect('/modules/upload-cyclone-forecast-data/')
    file_src_qry = """ select file_source from flood_forecast_files_sources """
    df = pds.read_sql(file_src_qry, connection)
    file_src_list = df.file_source.tolist()
    return render(request, 'grcmodule/upload_cyclone_forecast_files_form.html',
                  {'file_src_list': file_src_list})


@login_required
def cyclone_eap_analysis(request):
    """
    :param request:
    :return: cyclone eap analysis
    """
    qry = """ select file_source from cyclone_index_files cif order by published_year desc limit 1 """
    df = pds.read_sql(qry,connection)
    file_source = df.file_source.tolist()[0]
    return render(request, 'grcmodule/cyclone_eap_analysis.html', {'file_source': file_source})

@csrf_exempt
def cyclone_wind_speed_data(request):
    """
    :param   request:
    :return: table and map data with current wind speed
    """
    qry = """
        with sht as(select union_code,watchtime current_day,wind_speed from cyclone_data_current fdc where watchtime::date = (select distinct watchtime::date from cyclone_data_current order by watchtime limit 1))
        select fgd.*,sht.* from cyclone_geo_data fgd left join sht on fgd.union_code  = sht.union_code where fgd.index_file_id  = (select id from cyclone_index_files fif order by published_year desc limit 1 )
    """
    df = pds.read_sql(qry, connection)
    df['current_day'] = df['current_day'].astype(str)
    df = df.to_dict(orient='records')
    df_obj = {}
    var_list = []
    # wind speed map
    for x in df:
        df_obj[str(x["union_code"])] = float(x["wind_speed"])\
            if x["wind_speed"] is not None else 0
        var_list.append(float(x["wind_speed"]))\
            if x["wind_speed"] is not None else 0

    curr_date = ''
    if len(df):
        curr_date = df[0]['current_day']
    data = json.dumps({
        'df': df,
        'df_obj': df_obj,
        'var_list': var_list,
        'curr_date': curr_date
    })
    return HttpResponse(data)

@csrf_exempt
def cyclone_impact_data(request):
    """
    :param request:
    :return: table and map data with current day wind speed and impact
    """
    qry = """
        with sht as(select union_code,watchtime current_day,wind_speed,round(normalized_impact::numeric,2)::text  as impact from cyclone_data_current fdc where watchtime::date = (select distinct watchtime::date from cyclone_data_current order by watchtime limit 1))
        select fgd.*,sht.* from cyclone_geo_data fgd left join sht on fgd.union_code  = sht.union_code where impact::float > 0.25 and fgd.index_file_id  = (select id from cyclone_index_files fif order by published_year desc limit 1 )
        """
    df = pds.read_sql(qry, connection)
    df['current_day'] = df['current_day'].astype(str)
    df = df.to_dict(orient='records')
    df_impact = {}
    impact_list = []

    qry = """
            with sht as(select union_code,watchtime current_day,wind_speed,case when normalized_impact::float >= 0 and normalized_impact::float < 0.25 then round(impact::numeric,2)::text else round(normalized_impact::numeric,2)::text end  impact from cyclone_data_current fdc where watchtime::date = (select distinct watchtime::date from cyclone_data_current order by watchtime limit 1))
            select fgd.*,sht.* from cyclone_geo_data fgd left join sht on fgd.union_code  = sht.union_code where fgd.index_file_id  = (select id from cyclone_index_files fif order by published_year desc limit 1 )
           """
    df_map = pds.read_sql(qry, connection)
    df_map = df_map.to_dict(orient='records')

    # impact map
    for y in df_map:
        df_impact[y["union_code"]] = float(y["impact"])\
            if y["impact"] is not None else 0
        impact_list.append(float(y["impact"]))\
            if y["impact"] is not None else 0

    curr_date = ''
    if len(df):
        curr_date = df[0]['current_day']
    data = json.dumps({
        'df': df,
        'df_impact': df_impact,
        'impact_list': impact_list,
        'curr_date': curr_date
    })
    return HttpResponse(data)


@csrf_exempt
def cyclone_potential_data(request):
    """
    :param request:
    :return: table and map data with current day wind speed,
             impact , vulnerability_index, potential_damage, potential_damage_rank
    """
    qry = """
        with sht as
        (select union_code,watchtime current_day,wind_speed,round(vulnaribity_index::numeric,2)::text vulnaribity_index,round(potential_damage::numeric,2)::text potential_damage,potential_damage_rank
        ,round(normalized_impact::numeric,2)::text impact from cyclone_data_current fdc where watchtime::date = (select distinct watchtime::date from cyclone_data_current order by watchtime limit 1))
        select fgd.*,sht.*
        from cyclone_geo_data fgd left join sht on fgd.union_code  = sht.union_code
        where  impact::float > 0.25 and fgd.index_file_id  = (select id from cyclone_index_files fif order by published_year desc limit 1 )
        """
    df = pds.read_sql(qry, connection)
    df['current_day'] = df['current_day'].astype(str)
    df = df.to_dict(orient='records')

    df_potential = {}
    potential_list = []
    df_rank = {}
    df_impact = {}

    # potential map
    for y in df:
        df_potential[y["union_code"]] = float(y["potential_damage"]) \
            if y["potential_damage"] is not None else 0
        df_rank[y["union_code"]] = float(y["potential_damage_rank"]) \
            if y["potential_damage_rank"] is not None else 0
        df_impact[y["union_code"]] = float(y["impact"]) \
            if y["impact"] is not None else 0
        potential_list.append(float(y["potential_damage"])) \
            if y["potential_damage"] is not None else 0

    curr_date = ''
    if len(df):
        curr_date = df[0]['current_day']
    data = json.dumps({
        'df': df,
        'df_potential': df_potential,
        'df_rank': df_rank,
        'df_impact': df_impact,
        'potential_list': potential_list,
        'curr_date': curr_date
    })
    return HttpResponse(data)

@login_required
def storm_eap_analysis(request):
    """
    :param request:
    :return: storm eap analysis
    """
    qry = """ select file_source from cyclone_index_files cif order by published_year desc limit 1 """
    df = pds.read_sql(qry, connection)
    file_source = df.file_source.tolist()[0]
    return render(request, 'grcmodule/storm_eap_analysis.html', {'file_source': file_source})

@csrf_exempt
def storm_surge_data(request):
    """
    :param   request:
    :return: table and map data with current day storm surge
    """
    qry = """
        with sht as(select union_code,watchtime current_day,storm_surge from storm_data_current fdc where watchtime::date = (select distinct watchtime::date from storm_data_current order by watchtime limit 1))
        select fgd.*,sht.* from cyclone_geo_data fgd 
        left join sht on fgd.union_code  = sht.union_code where fgd.index_file_id  = (select id from cyclone_index_files fif 
        order by published_year desc limit 1 )
    """
    df = pds.read_sql(qry, connection)
    df['current_day'] = df['current_day'].astype(str)
    df = df.to_dict(orient='records')
    df_obj = {}
    var_list = []
    # wind speed map
    for x in df:
        df_obj[str(x["union_code"])] = float(x["storm_surge"])\
            if x["storm_surge"] is not None else 0
        var_list.append(float(x["storm_surge"]))\
            if x["storm_surge"] is not None else 0

    curr_date = ''
    file_source = ''
    if len(df):
        curr_date = df[0]['current_day']
    data = json.dumps({
        'df': df,
        'df_obj': df_obj,
        'var_list': var_list,
        'curr_date': curr_date
    })
    return HttpResponse(data)

@csrf_exempt
def storm_impact_data(request):
    """
    :param   request:
    :return: table and map data with current day storm surge and impact
    """
    qry = """
        with sht as(select union_code,watchtime current_day,storm_surge,round(normalized_impact::numeric,2)::text as impact from storm_data_current fdc where watchtime::date = (select distinct watchtime::date from storm_data_current order by watchtime limit 1))
        select fgd.*,sht.* from cyclone_geo_data fgd left join sht on fgd.union_code  = sht.union_code where impact::float > 0.25 and fgd.index_file_id  = (select id from cyclone_index_files fif order by published_year desc limit 1 )
        """
    df = pds.read_sql(qry, connection)
    df['current_day'] = df['current_day'].astype(str)
    df = df.to_dict(orient='records')
    df_impact = {}
    impact_list = []

    qry = """
            with sht as(select union_code,watchtime current_day,storm_surge,case when normalized_impact::float >= 0 and normalized_impact::float < 0.25 then round(impact::numeric,2)::text else round(normalized_impact::numeric,2)::text end  impact from storm_data_current fdc where watchtime::date = (select distinct watchtime::date from storm_data_current order by watchtime limit 1))
            select fgd.*,sht.* from cyclone_geo_data fgd left join sht on fgd.union_code  = sht.union_code where fgd.index_file_id  = (select id from cyclone_index_files fif order by published_year desc limit 1 )
           """
    df_map = pds.read_sql(qry, connection)
    df_map = df_map.to_dict(orient='records')

    # impact map
    for y in df_map:
        df_impact[y["union_code"]] = float(y["impact"])\
            if y["impact"] is not None else 0
        impact_list.append(float(y["impact"]))\
            if y["impact"] is not None else 0

    curr_date = ''
    if len(df):
        curr_date = df[0]['current_day']
    data = json.dumps({
        'df': df,
        'df_impact': df_impact,
        'impact_list': impact_list,
        'curr_date': curr_date
    })
    return HttpResponse(data)


@csrf_exempt
def storm_potential_data(request):
    """
    :param   request:
    :return: table and map data with current day storm surge,
             impact , vulnerability_index, potential_damage, potential_damage_rank
    """
    qry = """
        with sht as
        (select union_code,watchtime current_day, storm_surge,round(vulnaribity_index::numeric,2)::text vulnaribity_index,round(potential_damage::numeric,2)::text potential_damage, potential_damage_rank
        ,round(normalized_impact::numeric,2)::text impact from storm_data_current fdc where watchtime::date = (select distinct watchtime::date from storm_data_current order by watchtime limit 1))
        select fgd.*,sht.*
        from cyclone_geo_data fgd left join sht on fgd.union_code  = sht.union_code
        where impact::float > 0.25 and fgd.index_file_id  = (select id from cyclone_index_files fif order by published_year desc limit 1 )
        """
    df = pds.read_sql(qry, connection)
    df['current_day'] = df['current_day'].astype(str)
    df = df.to_dict(orient='records')

    df_potential = {}
    potential_list = []
    df_rank = {}
    df_impact = {}

    # potential map
    for y in df:
        df_potential[y["union_code"]] = float(y["potential_damage"]) \
            if y["potential_damage"] is not None else 0
        df_rank[y["union_code"]] = float(y["potential_damage_rank"]) \
            if y["potential_damage_rank"] is not None else 0
        df_impact[y["union_code"]] = float(y["impact"]) \
            if y["impact"] is not None else 0
        potential_list.append(float(y["potential_damage"])) \
            if y["potential_damage"] is not None else 0

    curr_date = ''
    if len(df):
        curr_date = df[0]['current_day']
    data = json.dumps({
        'df': df,
        'df_potential': df_potential,
        'df_rank': df_rank,
        'df_impact': df_impact,
        'potential_list': potential_list,
        'curr_date': curr_date
    })
    return HttpResponse(data)

@login_required
def detail_flood_index_files(request, file_id):
    """
    :param request:
    :param file_id:
    :return: table and map of requested index file
    """
    qry = """
    with t as (
    select union_code,vulnaribity_index from flood_data_history where id = any(select distinct  first_value(id)over(PARTITION by union_code ORDER by date_of_operation desc) from flood_data_history where index_file_id::int = """ +str(file_id)+ """)
    ), r as (
    select div_name,dist_name,upz_name,union_name,union_code, category_label from flood_geo_data fgd where index_file_id::int  = """ +str(file_id)+ """
    )select div_name,dist_name,upz_name,union_name,t.union_code,category_label,round(vulnaribity_index::numeric,2)::text vulnaribity_index from t,r where t.union_code = r.union_code
    """
    df = pds.read_sql(qry, connection)

    # index table data
    df = df.to_dict(orient='records')

    # index map
    df_obj = {}
    var_list = []
    for x in df:
        df_obj[str(x["union_code"])] = float(x["vulnaribity_index"])\
            if x["vulnaribity_index"] is not None else 0
        var_list.append(float(x["vulnaribity_index"]))\
            if x["vulnaribity_index"] is not None else 0

    lat_date_qry = """ select to_char(added_on,'YYYY-MM-DD HH24:MI:SS') added_on from flood_index_files order by added_on desc limit 1  """
    latest_date = __db_fetch_single_value(lat_date_qry)
    print(latest_date)
    data = json.dumps({
        'df': df,
        'df_obj': df_obj,
        'var_list': var_list,
        'latest_date': latest_date
    })
    return render(request,'grcmodule/detail_flood_index_files.html', {'data': data})


@login_required
def detail_cyclone_index_files(request, file_id):
    """
    :param request:
    :param file_id:
    :return: table and map of requested index file
    """
    # check where is v-index
    chk_qry = """ select id from cyclone_data_history where index_file_id::int ="""+str(file_id)+""" limit 1 """
    df = pds.read_sql(chk_qry,connection)
    if not df.empty:
        strs = 'cyclone'
    else:
        strs = 'storm'

    qry = """
    with t as (
    select union_code,vulnaribity_index from """+strs+"""_data_history where id = any(select distinct  first_value(id)over(PARTITION by union_code ORDER by date_of_operation desc) from """+strs+"""_data_history where index_file_id::int = """ +str(file_id)+ """)
    ), r as (
    select div_name,dist_name,upz_name,union_name,union_code, zone_label from cyclone_geo_data fgd where index_file_id::int  = """ +str(file_id)+ """
    )select div_name,dist_name,upz_name,union_name,t.union_code,zone_label,round(vulnaribity_index::numeric,2)::text vulnaribity_index from t,r where t.union_code = r.union_code
    """
    print(qry)
    df = pds.read_sql(qry, connection)

    # index table data
    df = df.to_dict(orient='records')

    # index map
    df_obj = {}
    var_list = []
    for x in df:
        df_obj[str(x["union_code"])] = float(x["vulnaribity_index"])\
            if x["vulnaribity_index"] is not None else 0
        var_list.append(float(x["vulnaribity_index"]))\
            if x["vulnaribity_index"] is not None else 0

    lat_date_qry = """ select to_char(added_on,'YYYY-MM-DD HH24:MI:SS') added_on from cyclone_index_files order by added_on desc limit 1  """
    latest_date = __db_fetch_single_value(lat_date_qry)
    print(latest_date)
    data = json.dumps({
        'df': df,
        'df_obj': df_obj,
        'var_list': var_list,
        'latest_date': latest_date
    })
    return render(request,'grcmodule/detail_cyclone_index_files.html', {'data': data})

@login_required
def flood_archive_list(request):
    """
    :param request:
    :return: flood archive list
    """
    return render(request, 'grcmodule/flood_archive_list.html')

@csrf_exempt
def get_flood_archive_list(request):
    """
    :param request: ajax call for archive data
    :return:  filtered data according to from and to date
    """
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    user_id = request.user.id
    query = """ select id,file_name,file_type,substring(file_location from position('static' in file_location)-1) file_location,(select username from auth_user where id = added_by::int)added_by,
                to_char(added_on,'DD/MM/YYYY HH24:MI') added_on,(select file_source
                from flood_index_files fif  where id = index_file_id::int) from flood_archive_files faf 
                where added_on::date between  '"""+str(from_date)+"""' and '"""+str(to_date)+"""'
             """
    data = json.dumps(__db_fetch_values_dict(query), default=decimal_date_default)
    return HttpResponse(data)

@login_required
@csrf_exempt
def delete_flood_archive_files(request,file_id):
    """
    :param request:
    :param file_id:
    :function : delete data from tables flood_archive_files and flood_archive_data
    :return: deleted list of archive data
    """
    qry = """ select substring(file_location from position('static' in file_location)-1) file_loc from flood_archive_files where id = """+str(file_id)
    df = pds.read_sql(qry,connection)
    if not df.empty:
        path = df.file_loc.tolist()[0]
        os.remove(path)
    qry = """ delete from flood_archive_files where id = """ + str(file_id)
    __db_commit_query(qry)
    return HttpResponseRedirect('/modules/flood-archive-files/')

@login_required
def cyclone_archive_list(request):
    """
    :param request:
    :return: cyclone archive list
    """
    return render(request, 'grcmodule/cyclone_archive_list.html')

@csrf_exempt
def get_cyclone_archive_list(request):
    """
    :param request: ajax call for archive data
    :return:  filtered data according to from and to date
    """
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    user_id = request.user.id
    query = """ select id,file_name,file_type,substring(file_location from position('static' in file_location)-1) file_location,(select username from auth_user where id = added_by::int)added_by,
                to_char(added_on,'DD/MM/YYYY HH24:MI') added_on,(select file_source
                from cyclone_index_files fif  where id = index_file_id::int),1 as archive_type from cyclone_archive_files faf 
                where added_on::date between  '"""+str(from_date)+"""' and '"""+str(to_date)+"""'
                union 
                select id,file_name,file_type,substring(file_location from position('static' in file_location)-1) file_location,(select username from auth_user where id = added_by::int)added_by,
                to_char(added_on,'DD/MM/YYYY HH24:MI') added_on,(select file_source
                from cyclone_index_files fif  where id = index_file_id::int),2 as archive_type from storm_archive_files faf 
                where added_on::date between  '"""+str(from_date)+"""' and '"""+str(to_date)+"""'
             """
    data = json.dumps(__db_fetch_values_dict(query), default=decimal_date_default)
    return HttpResponse(data)

@login_required
@csrf_exempt
def delete_cyclone_archive_files(request,file_id,file_type):
    """
    :param request:
    :param file_id  , file_type : file_type = 1 is cyclone, 2 is storm
    :function : delete data from tables cyclone_archive_files and cyclone_archive_data
    :return: deleted list of archive data
    """
    if file_type == '1':
        qry = """ select substring(file_location from position('static' in file_location)-1) file_loc from cyclone_archive_files where id = """+str(file_id)
        df = pds.read_sql(qry,connection)
        if not df.empty:
            path = df.file_loc.tolist()[0]
            os.remove(path)
        qry = """ delete from cyclone_archive_files where id = """ + str(file_id)
        __db_commit_query(qry)
    elif file_type == '2':
        qry = """ select substring(file_location from position('static' in file_location)-1) file_loc from storm_archive_files where id = """+str(file_id)
        df = pds.read_sql(qry,connection)
        if not df.empty:
            path = df.file_loc.tolist()[0]
            os.remove(path)
        qry = """ delete from storm_archive_files where id = """ + str(file_id)
        __db_commit_query(qry)
    return HttpResponseRedirect('/modules/cyclone-archive-files/')