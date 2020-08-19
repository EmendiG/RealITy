from django.http import HttpResponse
from django.shortcuts import render
from .models import Post
from .forms import GetPriceForm

# Create your views here.

def index(request):
    context = {
        'title': 'RealityWeb',
        'nieruchomosci': Post.objects.all()
    }
    return render(request, 'home/index.html', context)

def home(request):
    return render(request, 'miasta/Warszawa.html')

def about(request):
    return render(request, 'home/about.html', {'title':'About RealityWeb'})


def show_map2(request):
    import jinja2
    import folium
    class CircleMarkerEdited(folium.ClickForMarker):
        folium.ClickForMarker._template = jinja2.Template(u"""
                {% macro script(this, kwargs) %}
                    function newMarker(e){
                        
                        var DomIcon = L.Icon.extend({
                            options: {
                               iconSize:     [30, 50],
                               iconAnchor:   [15, 50],
                               popupAnchor: [0, -50],
                            }
                        });
                        var domekIcon = new DomIcon({
                            iconUrl: 'static/images/domek.png'
                        });
                        
                        var new_mark = L.marker().setIcon(domekIcon).setLatLng(e.latlng).addTo({{this._parent.get_name()}});  
                        new_mark.dragging.enable();
                        new_mark.on('dblclick', function(e){ {{this._parent.get_name()}}.removeLayer(e.target)})
                        var lat = e.latlng.lat.toFixed(4),
                            lng = e.latlng.lng.toFixed(4);
                        new_mark.bindPopup({{ this.popup }});
                    };

                    {{this._parent.get_name()}}
                    .on("contextmenu",  newMarker )
                {% endmacro %}
                """)  # noqa


        def __init__(self, popup=None):
            super().__init__()
            self._name = 'CircleMarkerEdited'

            if popup:
                self.popup = ' '.join([f'"Latitude: " + lat + "<br>Longitude: " + lng + "<br>Nieruchomosc"'])
            else:
                self.popup = '"Latitude: " + lat + "<br>Longitude: " + lng '


    #creation of map comes here + business logic
    m = folium.Map([52.237, 21.017], zoom_start=10)
    CircleMarkerEdited(popup='t').add_to(m)
    m = m._repr_html_()  # updated
    context = {'my_map': m,
               'title':'Map'}

    return render(request, 'miasta/map.html', context)

# https://django-map-widgets.readthedocs.io/en/latest/
# https://stackoverflow.com/questions/21387432/add-marker-on-a-map-and-catch-the-point-value-to-a-django-form-ajax-geodjango
# https://stackoverflow.com/questions/21415765/passing-value-to-a-form-input-field-inside-a-jquery-dialogbox

def show_map(request):

    form = GetPriceForm(request.POST or None)
    if form.is_valid():
        form.save()
    context = {
               'title': 'Map',
               'form': form}
    return render(request, 'miasta/map.html', context)

