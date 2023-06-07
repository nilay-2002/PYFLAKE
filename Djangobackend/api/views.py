from django.shortcuts import render
from .serializers import UserSerializer
from rest_framework.generics import ListAPIView
from .models import User
from django.db import connection
from django.shortcuts import render
import requests
from django.http import HttpResponse
from . import models
from sqlite3 import Cursor
import snowflake.connector
import os
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa 
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

    
def wherecond(where_col , where_op , where_val , where_cond):
     str1 = []
     where_cond.append(' ')
     for i in range(len(where_col)):
        str1.append(where_col[i])
        str1.append(where_op[i])
        str1.append(where_val[i])
        str1.append(where_cond[i])
     str1 = str1[0:-1] 
     str2 = ' '.join(str1)
     return str2
 

class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


def dictfetchall(cursor):
    desc = cursor.description
    return[
            dict(zip([col[0] for col in desc], row ))
            for row in cursor.fetchall()
    ]


@csrf_exempt
def establishConn(request):
    if request.method == "POST":
        data = request.body
        details = json.loads(data)
        # print(request.body)
        user = details['username']
        account = details['account']
        warehouse = details['warehouse']
        database = details['database']
        role = details['role']
        schema = details['schema']
        password = details['password']
        ctx = snowflake.connector.connect(
                            user= user, 
                            account= account,
                            # private_key=pkb, 
                            warehouse = warehouse,
                            database = database,
                            role = role,
                            schema = schema,
                            password = password )
        
        
        if ctx:
            return ctx
 
        else:                            
            return JsonResponse({'error' : "Enter Correct details"})

    else:
        return JsonResponse({400: 'Invalid request method'})

@csrf_exempt
def column_names(request):
    if request.method =='POST':
        try:
            data = request.body
            details = json.loads(data)
            table_name = details['table']
            ctx = establishConn(request)
            query = f'show columns in {table_name}'
            result = ctx.cursor().execute(query)
            a = dictfetchall(result)
            col_names = []
            for item in a: 
                init_colname = item['column_name']
                col_names.append(init_colname)
            context = {
                'columns' : col_names
            }
            return JsonResponse(context)
        
        except Exception as e:
            return JsonResponse({
                401 : 'Wrong Credentials'
            })
    
    else:
        return JsonResponse({400: 'Invalid request method'})

@csrf_exempt
def snowflakeconn(request):
    if request.method == "POST":
        data = request.body
        details = json.loads(data)
        # print(request.body)
        user = details['username']
        account = details['account']
        warehouse = details['warehouse']
        database = details['database']
        role = details['role']
        schema = details['schema']
        password = details['password']
        ctx = snowflake.connector.connect(
                            user= user, 
                            account= account, 
                            warehouse = warehouse,
                            database = database,
                            role = role,
                            schema = schema,
                            password = password )
        result1 = ctx.cursor().execute('show tables')
        tab = dictfetchall(result1)
        tab_names = []
        for item in tab: 
            init_tabname = item['name']
            tab_names.append(init_tabname)
        print(tab_names)
        
        context = {
            'tables' : tab_names
        }
        return JsonResponse(context)


      
    else:
        return JsonResponse({400: 'Invalid request method'})

@csrf_exempt
def getreq(request):
    # select * from movie where ID = 1
    if request.method == 'POST':
        data = request.body
        details = json.loads(data)
        a = details['where']
        where_col = a['column']
        where_op = a['operator']
        where_val = a['value']
        where_cond = a['condition']
        columnNames = details['columns']
        table = details['table']
        where = list(a.values())
        try:
            if columnNames == []:
                if where_col == []:
                    ctx = establishConn(request)
                    query = f'select * from {table}'
                    result = ctx.cursor().execute(query)

                    datas = dictfetchall(result)
                    data = { 
                    'result' : datas
                    }
                    return JsonResponse(data)
                    
                else:   
                    ctx = establishConn(request)
                    str2 = wherecond(where_col , where_op , where_val , where_cond)
                    query1 = f'select * from {table} where' +' '+ str2
                    print(query1)
                    result1 = ctx.cursor().execute(query1)
                    datas = dictfetchall(result1)
                    data = { 
                    'result' : datas
                    }
                    return JsonResponse(data)


            else:
                if where_col == []:
                    ctx = establishConn(request)
                    seprated1 = ', '.join(columnNames)
                    queryz = f'select {seprated1} from {table} '
                    result2 = ctx.cursor().execute(queryz)
                    datas = dictfetchall(result2)
                    data = { 
                        'result' : datas
                        }
                    return JsonResponse(data)  
                else:

                    ctx = establishConn(request)
                    seprated1 = ', '.join(columnNames)
                    str2 = wherecond(where_col , where_op , where_val , where_cond)    
                    queryz = f'select {seprated1} from {table} where '
                    f_query = queryz + str2
                    print(f_query)
                    result2 = ctx.cursor().execute(f_query)
                    datas = dictfetchall(result2)
                    data = { 
                        'result' : datas
                        }
                    return JsonResponse(data)
                
        except Exception as e:
            return JsonResponse({
                401 : 'Wrong Credentials',
                'error' : e
            })


    else:
        return JsonResponse({400: 'Invalid request method'})

@csrf_exempt
def updatereq(request):
    # UPDATE table_name
    # SET column1 = value1, column2 = value2, ...
    # WHERE condition;
    if request.method == 'POST':
        data = request.body
        details = json.loads(data)
        columns = details['column']
        a = details['where']      
        where_col = a['column']
        where_op = a['operator']
        where_val = a['value']
        where_cond = a['condition']
        table = details['table']  
        updateval = details['updatedValue']  
        where = list(a.values())
        
        str1 = wherecond(where_col , where_op , where_val , where_cond)    
        query1 = f'update {table} set {columns} = {updateval}  where ' + str1
        print(query1)
        ctx = establishConn(request)            
        result = ctx.cursor().execute(query1)
        
        datas = dictfetchall(result)
        data1 = {'result' : datas}
        print(data1)
        return JsonResponse(data1)
    
    else:
        return JsonResponse({400: 'Invalid request method'})
    

@csrf_exempt
def insertreq(request):
    # POST
    # INSERT INTO table_name (column1, column2, column3, ...)
    # VALUES (value1, value2, value3, ...);
    if request.method == 'POST':
        data = request.body
        details = json.loads(data)        
        print(details)
        table = details['table']
        columns = details['columns']
        values = details['value']
        try:
            str1 = ', '.join(columns)    
            str2 = ', '.join(values)
            ctx = establishConn(request)
            query = f'INSERT INTO {table} ({str1}) values ({str2}) '
            print(query)
            result = ctx.cursor().execute(query)
            
            datas = dictfetchall(result)
            data = { 
                    'result' : datas
                    }
            return JsonResponse(data)
        
        except Exception as e:
            return JsonResponse({
                401 : 'Wrong Credentials',
                'error' : e
            })
    
    else:
        return JsonResponse({400: 'Invalid request method'})
    
@csrf_exempt
def deletereq(request):
    # DELETE FROM table_name WHERE condition;
    if request.method == 'POST':
        data = request.body
        details = json.loads(data)
        table = details['table']
        a = details['where']
        where_col = a['column']
        where_op = a['operator']
        where_val = a['value']
        where_cond = a['condition']
        try:
            where = list(a.values())
            str1 = wherecond(where_col , where_op , where_val , where_cond)    

            ctx = establishConn(request)

            if  str1 == '':
                return JsonResponse({
                    'error' : 'Cannot delete entire table'
                })
            else:
                query = f'DELETE FROM {table} where ' + str1
                result1 = ctx.cursor().execute(query)
                datas = dictfetchall(result1)
                data = { 
                'result' : datas
                }
                return JsonResponse(data)
        except Exception as e:
            return JsonResponse({
                401 : 'Wrong Credentials',
                'error' : e
            })

    else:
        return JsonResponse({'400': 'Invalid request method'})


@csrf_exempt
def raw(request):
    if request.method == 'POST':
        data = request.body
        print('\n\n\n\n\n****')
        # print(request.body)
        details = json.loads(data)
        print(details)
        query = details['query'] 
        print(query) 
        try:
            ctx = establishConn(request)
            X = 'drop'
            Y = 'truncate'
            str1 = query.lower()
            if X in str1:
                return JsonResponse({'error' : 'Cannot drop entire table'})
            elif Y in str1:
                return JsonResponse({'error' : 'Cannot truncate entire table'})
            else:
                result1 = ctx.cursor().execute(query)
                datas = dictfetchall(result1)
                data = { 
                'result' : datas
                }
                return JsonResponse(data)
        except Exception as e:
            return JsonResponse({
                401 : 'Wrong Credentials',
                'error' : e
            })
        
    else:
        return JsonResponse({400: 'Invalid request method'})



