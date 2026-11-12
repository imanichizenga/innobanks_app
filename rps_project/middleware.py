# # middleware.py

# from django.http import HttpResponseRedirect

# class RedirectToCustomDomainMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # This code runs before the view is processed
#         if not request.get_host() == "innobanks.store":
#             return HttpResponseRedirect("https://innobanks.store" + request.path)
#         response = self.get_response(request)
#         return response
