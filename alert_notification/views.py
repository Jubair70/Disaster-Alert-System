# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import decimal
import json
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.mail import get_connection, EmailMultiAlternatives
from django.db import connection
from django.http.response import JsonResponse
from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import (
    HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound,
    HttpResponseBadRequest, HttpResponse)
from django.views.decorators.csrf import csrf_exempt

from grc import settings


def __db_commit_query(query):
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()


def __db_insert_query(query):
    """
    function __db_insert_query executes query and returns insert id
    Args:
        query: query to be executed
        dbname: intended database for this operation

    Returns:
        return insert id
    """
    cursor = connection.cursor()
    cursor.execute(query)
    fetch_val = cursor.fetchone()
    cursor.close()
    return fetch_val[0]


def __db_fetch_values_dict(query):
    cursor = connection.cursor()
    cursor.execute(query)
    fetchVal = dictfetchall(cursor)
    cursor.close()
    return fetchVal


def dictfetchall(cursor):
    desc = cursor.description
    return [
        OrderedDict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()]


def decimal_date_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return obj
    raise TypeError


@login_required
def create_alert_notification(request):
    """
        Returns on a html page.

        Argument: request.

        Return: Returns on 'alert_notification/create_alert_notification_form.html' page.
    """
    return render(request, 'alert_notification/create_alert_notification_form.html')


@login_required
def sms_queue_list(request):
    """
        This function is for fetching all data from 'sms_queue' table and returns 'alert_notification/sms_queue.html'
        page with data as JSON format.

        Argument: request

        Return: Returns on 'alert_notification/sms_queue.html' page with 'data' as JSON format.
    """
    sms_queue_list_query = """ select * from sms_queue """
    data = json.dumps(__db_fetch_values_dict(sms_queue_list_query), default=decimal_date_default)
    return render(request, 'alert_notification/sms_queue.html', {'data': data})


@login_required
def saved_message_list(request):
    """
        This function is for fetching all data from 'alert_sms' table and returns
        'alert_notification/saved_message_list.html'
        page with data as JSON format.

        Argument: request

        Return: Returns on 'alert_notification/saved_message_list.html' page with 'data' as JSON format.
    """
    # saved_message_list_query = """ select alert_sms.id, alert_sms.text, alert_sms.description, alert_sms.created_on, alert_sms.stage_id, alert_sms.message_type, STRING_AGG (t.team_name, ';') team_list, is_sent_or_saved from alert_sms left join alert_sms_teams ast on alert_sms.id = ast.alert_sms_id left join teams t on ast.team_id = t.id GROUP BY alert_sms.id """
    saved_message_list_query = """ select count(distinct r.id) rec_id_count, alert_sms.id, alert_sms.text, \
                                alert_sms.description, alert_sms.created_on, alert_sms.stage_id, alert_sms.process_type, \
                                alert_sms.message_type, STRING_AGG (distinct t.team_name, ';') team_list, \
                                is_sent_or_saved from alert_sms left join alert_sms_teams ast on alert_sms.id = \
                                ast.alert_sms_id left join teams t on ast.team_id = t.id left join recepients_teams \
                                rt on t.id = rt.team_id left join recepients r on rt.recepient_id = r.id GROUP BY \
                                alert_sms.id """
    data = json.dumps(__db_fetch_values_dict(saved_message_list_query), default=decimal_date_default)
    return render(request, 'alert_notification/saved_message_list.html', {'data': data})


@login_required
def specific_saved_message(request, msg_id):
    """
    This function is fetching a specific saved message data from joining 'alert_sms', 'alert_sms_teams' and 'teams'
    tables filtering with 'alert_sms_teams.alert_sms_id (msg_id)'.

    Argument: request, msg_id

    Return: specific message data 'data' as JSON format.
    """
    specific_message_query = """ select alert_sms.id, alert_sms.text, alert_sms.description, alert_sms.created_on, \
                                alert_sms.stage_id, alert_sms.message_type, alert_sms.process_type, \
                                alert_sms.disaster_type, STRING_AGG (t.team_name, ';') team_list, array_agg(t.id) \
                                team_id_list  from alert_sms left join alert_sms_teams ast on alert_sms.id = \
                                ast.alert_sms_id left join teams t on ast.team_id = t.id where alert_sms_id = \
                                """ +msg_id+ """ GROUP BY alert_sms.id """
    data = json.dumps(__db_fetch_values_dict(specific_message_query), default=decimal_date_default)
    return HttpResponse(data)


@csrf_exempt
def sms_queue_insert(request):
    """
        This function is for inserting message into 'sms_queue' table. This function is working for two tasks:

        1.  For clicking 'send message' button the message inserting directly into 'sms_queue' table. But befor that
        it also inserting into 'alert sms' and 'alert_sms_teams' table with 'alert_sms.is_sent_or_saved' column value as '2 (which indecates
        that this data has been sent to the sms queue)'.

        Argument: request

        Return: Returns redirecting '/alert-notification/create-alert-notification/' page.


        2.  For clicking the send icon of 'save message history' table the message inserting into 'sms_queue' table.
        This data is already saved into 'alert_sms' table but after inserting into 'sms_queue' table also updating
        the 'alert_sms.is_sent_or_saved' column as (2) using same 'alert_sms.id'.

        Argument: request

        Return: Returns to ajax.

    """
    message_details = str(request.POST['message_details'])
    message_type = str(request.POST['message_type'])
    message = str(request.POST['message'])


    if request.POST.getlist('team-select[]'):
        team_list = request.POST.getlist('team-select[]')

    else:
        team_list = request.POST.getlist('team-select')

    uploaded_file_path = ""
    # print(" Before !")
    if 'message-file' in request.FILES:
        print(" nothing !")
        myfile = request.FILES['message-file']

        url = "static/alert-message-attachment/"
        fs = FileSystemStorage(location=url)
        uploaded_file_path = url + str(myfile.name)
        if fs.exists(str(myfile.name)):
            fs.delete(str(myfile.name))
        filename = fs.save(str(myfile.name), myfile)

    is_sent = 2
    if 'disaster_type' in request.POST:
        disaster_type = str(request.POST['disaster_type'])

    if 'process_type' in request.POST:
        process_type = str(request.POST['process_type'])

    if 'stage_id' in request.POST:
        stage_id = int(request.POST['stage_id'])

    if 'iddd' not in request.POST:
        print("new iddddddddd")
        ins_qry_alert_sms = """ INSERT INTO public.alert_sms
                                        (text, description, disaster_type, message_type, stage_id, is_sent_or_saved, \
                                        attachment_file_path, process_type)
                                        VALUES('""" + message + """', '""" + message_details + """', '""" \
                                        + disaster_type + """', '""" + message_type + """', """ + str(
                                        stage_id) + """, """ + str(is_sent) + """, '""" + uploaded_file_path + """', \
                                        '""" + process_type + """') returning id """

        alert_sms_id = __db_insert_query(ins_qry_alert_sms)

        for x in team_list:
            print ("x ========== ", int(x))
            ins_qry_recepient_team = """ INSERT INTO public.alert_sms_teams
                                        (alert_sms_id, team_id)
                                        VALUES(""" + str(alert_sms_id) + """, """ + str(x) + """) """

            __db_commit_query(ins_qry_recepient_team)


    recepient_number_or_email_list = []

    team_id_list = ''
    team = '('
    for x in team_list:
        # team_id_list.append(int(x))
        team += str(int(x)) + ', '

    team = team[0:-2]
    team += ')'
    team_id_list = str(team)

    msg_type = ''

    if message_type == 'email':
        recepients_info_query = """ select distinct recepients.email from recepients join recepients_teams rt on\
                                    recepients.id = rt.recepient_id where team_id in """ + str(team_id_list)
        msg_type = 'email'

    else:
        recepients_info_query = """ select distinct recepients.contact from recepients join recepients_teams rt on \
                                    recepients.id = rt.recepient_id where team_id in """ + str(team_id_list)
        msg_type = 'contact'

    data = __db_fetch_values_dict(recepients_info_query)

    for x in data:
        recepient_number_or_email_list.append(str(x[msg_type]))

    # print("recepient_list =========== ", recepient_number_or_email_list)

    if 'iddd' in request.POST:
        print("old Id 1")
        alert_sms_id = request.POST['iddd']

    for x in recepient_number_or_email_list:
        # print("rec ============== ", x);
        ins_qry_sms_query = """ INSERT INTO public.sms_queue

                                (recepint_num_or_email, message, description, message_type, status, alert_sms_id)
                                VALUES('""" + x + """', '""" + message + """', '""" + message_details + """', '""" \
                                + message_type + """', """ + str(0) + """, """ + str(alert_sms_id) + """) """

        __db_commit_query(ins_qry_sms_query)

    if 'iddd' in request.POST:
        print("old Id 2")
        saved_msg_id = request.POST['iddd']
        updt_message_qry = """ UPDATE public.alert_sms SET is_sent_or_saved=""" + str(2) + """ WHERE id = """ \
                           + saved_msg_id
        __db_commit_query(updt_message_qry)

        data = {
            'saved_msg_id': saved_msg_id,
        }

        return JsonResponse(data)

    return HttpResponseRedirect('/alert-notification/create-alert-notification/')


@csrf_exempt
def save_message(request):
    """
        This function is for inserting data into 'alert_sms' table as this is 'saved / not sent yet' message.
        Also inserting data into 'alert_sms_teams' table.

        Argument: Request

        Return: Returns redirecting '/alert-notification/saved-message/' page.

    """
    message_details = str(request.POST['message_details'])
    message_type = str(request.POST['message_type'])
    message = str(request.POST['message'])
    process_type = str(request.POST['process_type'])
    team_list = request.POST.getlist('team-select')
    disaster_type = str(request.POST['disaster_type'])
    stage_id = int(request.POST['stage_id'])

    uploaded_file_path = ""
    if 'message-file' in request.FILES:
        myfile = request.FILES['message-file']

        url = "static/alert-message-attachment/"
        fs = FileSystemStorage(location=url)
        uploaded_file_path = url + str(myfile.name)
        if fs.exists(str(myfile.name)):
            fs.delete(str(myfile.name))
        filename = fs.save(str(myfile.name), myfile)
    is_save = 1


    ins_qry_alert_sms = """ INSERT INTO public.alert_sms
                            (text, description, disaster_type, message_type, stage_id, is_sent_or_saved, \
                            attachment_file_path, process_type)
                            VALUES('""" + message + """', '""" + message_details + """', '""" + disaster_type + \
                            """', '""" + message_type + """', """ + str(stage_id) + """, """ + str(is_save) \
                            + """, '""" + uploaded_file_path + """', '""" + process_type + """') returning id """

    alert_sms_id = __db_insert_query(ins_qry_alert_sms)

    for x in team_list:
        print ("x ========== ", int(x))
        ins_qry_recepient_team = """ INSERT INTO public.alert_sms_teams
                                (alert_sms_id, team_id)
                                VALUES(""" + str(alert_sms_id) + """, """ + str(x) + """) """

        __db_commit_query(ins_qry_recepient_team)

    data = {
        'alert_sms_id': alert_sms_id,
    }

    return HttpResponseRedirect('/alert-notification/saved-message/')


def edit_message(request, msg_id):
    """
        This function is for editing saved messages by updating 'alert_sms' table and deleting old data from
        'alert_sms_teams' table and inserting new data into it.

        Argument: request, 'msg_id' as 'alert_sms.id'.

        Return: Returns 'alert_sms.id'.

    """
    edit_message_details = str(request.POST['edit_message_details'])
    edit_message_type = str(request.POST['edit_message_type'])
    edit_message = str(request.POST['edit_message'])
    edit_team_select = request.POST.getlist('edit-team-select')
    edit_disaster_type = str(request.POST['edit_disaster_type'])
    edit_stage_id = int(request.POST['edit_stage_id'])

    #, , , , , is_sent_or_saved
    updt_message_qry = """ UPDATE public.alert_sms SET text='""" + str(edit_message) + """', description='""" \
                       + str(edit_message_details) + """', disaster_type='""" + str(edit_disaster_type) + """', \
                       message_type='""" + str(edit_message_type) + """', stage_id=""" + str(edit_stage_id) + \
                       """ WHERE id = """ + msg_id
    __db_commit_query(updt_message_qry)

    del_msg_team_qry = """ delete from alert_sms_teams where alert_sms_id = """ + msg_id
    __db_commit_query(del_msg_team_qry)

    for x in edit_team_select:
        ins_qry_msg_team = """ INSERT INTO public.alert_sms_teams
                                (alert_sms_id, team_id)
                                VALUES(""" + str(msg_id) + """, """ + str(x) + """) """

        __db_commit_query(ins_qry_msg_team)

    data = {
        'message_id': msg_id
    }

    return JsonResponse(data)


def saved_message_delete(request, msg_id):
    """
        This function is for deleting saved message executing delete operation on 'alert_sms_teams' and 'alert_sms'
        tables.

        Argument: request, 'msg_id' as 'alert_sms.id'.

        Return: Redirecting '/alert-notification/saved-message/' page.

    """

    del_msg_team_qry = """ delete from alert_sms_teams where alert_sms_id = """ + msg_id
    __db_commit_query(del_msg_team_qry)

    del_msg_qry = """ delete from alert_sms where id = """ + msg_id
    __db_commit_query(del_msg_qry)

    data = {
        'message_id': msg_id
    }
    return HttpResponseRedirect('/alert-notification/saved-message/')


