from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from website import views
from website.views import HomeListView, AddRecordView, SignUpView, SearchResultsView, DeleteRecordView, UpdateRecordView, UpdateInformationView, AddNewOwnerView, Stats, LineChartNormView, LineChartJSONView, PieChartJSONView, RecordInfoView, LandingPageView
from website.models import Record

# Creates URLS for each page 
urlpatterns = [ 
    path('', views.HomeListView.as_view(), name='home'), # Each defined .as_view() since they are class based
    path('landingpage/', views.LandingPageView.as_view(), name='landing-page'),
    path('info/<int:pk>', views.RecordInfoView.as_view(), name='info'), # <int:pk> is the specific object that the page is accessing 
    path('delete/<int:pk>', DeleteRecordView.as_view(), name='record-delete'),
    path('update/<int:pk>', UpdateRecordView.as_view(), name='record-update'),
    path('admin/', admin.site.urls), # Default admin page for Django
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.SignUpView.as_view(), name='signup'), # Link inside of the already made accounts link
    path('accounts/updateinfo/<int:pk>', views.UpdateInformationView.as_view(), name='update-information'),
    path("add_record/", views.AddRecordView.as_view(), name="add_record"),
    path("search/", views.SearchResultsView.as_view(), name="search_results"),
    path("addowner/", views.AddOwnerView, name="add_owner"),
    path("addnewowner/", views.AddNewOwnerView, name="add_new_owner"),
    path("stats/", views.LineChartNormView.as_view(),  name="stats1"),
    path("stats/linegraph", views.LineChartJSONView.as_view(), name="line_chart_json"),
    path("stats/piegraph", views.PieChartJSONView.as_view(), name="pie_chart_json"),
]

# Option for debugging
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


