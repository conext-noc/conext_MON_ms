import json
import os
from dotenv import load_dotenv
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import generics
from mon.scripts.SM import summary_data
from mon.scripts.CA import alarms_data
from mon.scripts.DT import deactivates_data
from mon.scripts.VP import port_data
from mon.scripts.VT import all_clients

load_dotenv()


class MON(generics.GenericAPIView):
    def get(self, _):
        return Response({"message": "ms_running", "error": False}, 200)


# get with apikey to /summary?apiKey gives summarized data of olt => {active, deactivated, alarms}
class Summary(generics.GenericAPIView):
    def get(self, req):
        api_key = req.query_params.get("apiKey")
        print(api_key)
        if api_key != os.environ["CONEXT_KEY"]:
            return Response({"message": "Bad Request to server", "error": True}, 401)
        res = summary_data()
        if res["error"]:
            return Response(res, 202)
        return Response(res, 200)


# get with apiKey to /alarms?apiKey gives all the clients currently in a alarm state
class Alarms(generics.GenericAPIView):
    def get(self, req):
        api_key = req.query_params.get("apiKey")
        if api_key != os.environ["CONEXT_KEY"]:
            return Response({"message": "Bad Request to server", "error": True}, 401)
        res = alarms_data()
        if res["error"]:
            return Response(res, 202)
        return Response(res, 200)


# get with apiKey to /deactivates?apiKey gives all the clients currently in a deactivate state
class Deactivate(generics.GenericAPIView):
    def get(self, req):
        api_key = req.query_params.get("apiKey")
        if api_key != os.environ["CONEXT_KEY"]:
            return Response({"message": "Bad Request to server", "error": True}, 401)
        res = deactivates_data()
        if res["error"]:
            return Response(res, 202)
        return Response(res, 200)


# get with contract and apiKey to /traffic?contract&apiKey gives all the traffic currently in a client


# get with fsp and apiKey to /port?fsp&apiKey gives the current info of a specific port
class PortVerify(generics.GenericAPIView):
    def get(self, req):
        api_key = req.query_params.get("apiKey")
        if api_key != os.environ["CONEXT_KEY"]:
            return Response({"message": "Bad Request to server", "error": True}, 401)
        fsp = req.query_params.get("fsp").replace("-","/")
        olt = req.query_params.get("olt")
        res = port_data(fsp, olt)
        if res["error"]:
            return Response(res, 202)
        return JsonResponse(res)


# get all clients data from any OLT to /total?apiKey
class AllClients(generics.GenericAPIView):
    def get(self, req):
        api_key = req.query_params.get("apiKey")
        if api_key != os.environ["CONEXT_KEY"]:
            return Response({"message": "Bad Request to server", "error": True}, 401)
        res = all_clients()
        if res["error"]:
            return Response(res, 202)
        return Response(res, 200)
