# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import decimal
import json
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.mail import get_connection, EmailMultiAlternatives
from django.db import connection
from django.http.response import JsonResponse
from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import (
    HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound,
    HttpResponseBadRequest, HttpResponse)

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
def recepientlist(request):
    """
        function recepientlist fetches all recepient's data from joining 'recepients', 'recepients_teams' and
        'teams' table.

        Argument: request

        Returns: return into 'recepient_list/recepient_list.html' page with recepient's data as JSON format.
    """

    recepient_list_query = """ select recepients.id, recepients.organization, recepients.name, recepients.email, \
                            recepients.contact, recepients.date_added, STRING_AGG (t.team_name, ';') team_list  from recepients left join \
                            recepients_teams rt on recepients.id = rt.recepient_id left join teams t on rt.team_id = t.id GROUP BY \
                            recepients.id """
    # print("recepient_list_query ============== ", recepient_list_query)
    data = json.dumps(__db_fetch_values_dict(recepient_list_query), default=decimal_date_default)
    return render(request, 'recepient_list/recepient_list.html', {'data': data})


@login_required
def specific_recepient(request, rec_id):
    """
        function specific_recepient fetches a specific recepient's data filtering with the recepient's id from joining 'recepients', 'recepients_teams' and
        'teams' table.

        Argument: request, 'rec_id' as 'recepients.id'

        Returns:  return the specific recepient's data 'data' as JSON format.
    """
    specific_recepient_query = """ select recepients.*, STRING_AGG (t.team_name, ';') team_list, array_agg(t.id) \
                                team_id_list  from recepients left join recepients_teams rt on recepients.id = rt.recepient_id \
                                left join teams t on rt.team_id = t.id where recepient_id = """ + rec_id + """ GROUP BY recepients.id"""
    data = json.dumps(__db_fetch_values_dict(specific_recepient_query), default=decimal_date_default)
    return HttpResponse(data)


@login_required
def add_team(request):
    """
    This function inserts into 'teams' table for adding new team in database.

    Argument: request

    Return: Returns the new team name.
    """
    team_name = str(request.POST['team-name'])
    print("team_name ===== ", team_name)
    if team_name != '' or team_name is not None:
        ins_qry_team = """ INSERT INTO public.teams
                                (team_name)
                                VALUES('""" + team_name + """') """

        __db_commit_query(ins_qry_team)

    data = {
        'team_name': team_name
    }
    return JsonResponse(data)


def get_team_data(request):
    """
        This function fetches all team data 'teams' table and returns data as JSON format.

        Argument: request

        Return: Returns all team data 'data' as JSON format
    """
    query = """ select id, team_name from teams """
    print(query)
    data = json.dumps(__db_fetch_values_dict(query), default=decimal_date_default)
    return HttpResponse(data)


@login_required
def add_recepient(request):
    """
    This function is for adding new recepient executing insert query in 'recepients' table
    and also in 'recepients_teams' table because there is manytomany relationship bitween 'recepients' and
    'teams' tables.

    Argument: request

    Return: Returns recepient's id and name as 'data' as JSON format.
    """
    recepient_name = str(request.POST['recepient_name'])
    mobile_no = str(request.POST['mobile_no'])
    email = str(request.POST['email'])
    team = request.POST.getlist("team")
    organization = str(request.POST['organization'])

    ins_qry_recepient = """ INSERT INTO public.recepients
                            (name, email, contact, organization)
                            VALUES('""" + recepient_name + """', '""" + email + """', '""" + mobile_no + """', '""" + organization + """') returning id """

    recepient_id = __db_insert_query(ins_qry_recepient)
    print("recepient_id ============== ", recepient_id)

    for x in team:
        print ("x ========== ", int(x))
        ins_qry_recepient_team = """ INSERT INTO public.recepients_teams
                                (recepient_id, team_id)
                                VALUES(""" + str(recepient_id) + """, """ + str(x) + """) """

        __db_commit_query(ins_qry_recepient_team)

    data = {
        'recepient_id': recepient_id,
        'recepient_name': recepient_name
    }
    return JsonResponse(data)


@login_required
def edit_recepient(request, rec_id):
    """
        This function is for editing a recepient's data executing update query on 'recepients' table and deleting
         old data and inserting new data into 'recepients_teams' table.
         Return: Returns recepient's id.

         Argument: request, 'rec_id' as 'recepients.id'

         Return: Returns recepients's id
    """
    recepient_name = str(request.POST['edit_recepient_name'])
    mobile_no = str(request.POST['edit_mobile_no'])
    email = str(request.POST['edit_email'])
    team = request.POST.getlist("edit_team")
    organization = str(request.POST['edit_organization'])

    updt_recepient_qry = """ UPDATE public.recepients SET name='""" + str(recepient_name) + """', email='""" + str(
        email) + """', contact=""" + str(mobile_no) + """, organization='""" + str(
        organization) + """' WHERE id = """ + rec_id
    __db_commit_query(updt_recepient_qry)

    del_rec_tem_qry = """ delete from recepients_teams where recepient_id = """ + rec_id
    __db_commit_query(del_rec_tem_qry)

    for x in team:
        print ("x ========== ", int(x))
        ins_qry_recepient_team = """ INSERT INTO public.recepients_teams
                                (recepient_id, team_id)
                                VALUES(""" + str(rec_id) + """, """ + str(x) + """) """

        __db_commit_query(ins_qry_recepient_team)

    data = {
        'recepient_id': rec_id
    }

    return JsonResponse(data)


@login_required
def delete_recepient(request, rec_id):
    """
        This function is for deleting a recepient's data from 'recepients' table.
        Return: Returns recepient's id.

        Argument: request, 'rec_id' as 'recepients.id'

        Return: Returns recepients's id
    """
    print("del rec ============= ", rec_id)

    del_rec_tem_qry = """ delete from recepients_teams where recepient_id = """ + rec_id
    __db_commit_query(del_rec_tem_qry)

    del_rec_qry = """ delete from recepients where id = """ + rec_id
    __db_commit_query(del_rec_qry)

    data = {
        'recepient_id': rec_id,
    }
    return JsonResponse(data)
