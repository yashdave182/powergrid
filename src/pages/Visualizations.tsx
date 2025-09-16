import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from "recharts";
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from "react-leaflet";
import { LatLngExpression } from "leaflet";
import { BarChart3, Map, TrendingUp, Waves, Fish, Thermometer } from "lucide-react";
import { useState } from "react";
import "leaflet/dist/leaflet.css";

// Fix for default markers in react-leaflet
import L from "leaflet";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

let DefaultIcon = L.divIcon({
  html: `<div class="bg-blue-600 w-3 h-3 rounded-full border-2 border-white shadow-lg"></div>`,
  iconSize: [12, 12],
  className: "custom-div-icon",
});

L.Marker.prototype.options.icon = DefaultIcon;

const Visualizations = () => {
  const [selectedDataset, setSelectedDataset] = useState("temperature");

  // Sample data
  const temperatureData = [
    { month: "Jan", temp: 28.5, abundance: 45 },
    { month: "Feb", temp: 29.2, abundance: 52 },
    { month: "Mar", temp: 30.1, abundance: 38 },
    { month: "Apr", temp: 31.8, abundance: 41 },
    { month: "May", temp: 32.5, abundance: 35 },
    { month: "Jun", temp: 30.9, abundance: 48 },
  ];

  const speciesData = [
    { name: "Tuna", count: 45, color: "#0EA5E9" },
    { name: "Sardines", count: 32, color: "#10B981" },
    { name: "Mackerel", count: 28, color: "#F59E0B" },
    { name: "Anchovies", count: 25, color: "#EF4444" },
    { name: "Others", count: 18, color: "#8B5CF6" },
  ];

  const samplingStations = [
    { id: 1, name: "Station A", position: [12.9716, 77.5946] as LatLngExpression, temp: 29.5, species: 15 },
    { id: 2, name: "Station B", position: [10.8505, 76.2711] as LatLngExpression, temp: 28.8, species: 23 },
    { id: 3, name: "Station C", position: [9.9252, 78.1198] as LatLngExpression, temp: 30.2, species: 18 },
    { id: 4, name: "Station D", position: [11.1271, 75.3412] as LatLngExpression, temp: 27.9, species: 21 },
    { id: 5, name: "Station E", position: [8.5241, 76.9366] as LatLngExpression, temp: 31.1, species: 12 },
  ];

  const diversityData = [
    { parameter: "Shannon Index", value: 2.8, max: 4.0 },
    { parameter: "Simpson Index", value: 0.75, max: 1.0 },
    { parameter: "Species Richness", value: 45, max: 60 },
    { parameter: "Evenness", value: 0.82, max: 1.0 },
  ];

  return (
    <div className="min-h-screen bg-gradient-depth p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Data Visualizations</h1>
          <p className="text-muted-foreground">Interactive charts and maps for marine research data</p>
        </div>

        {/* Control Panel */}
        <Card className="mb-6 shadow-float">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Visualization Controls</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="lg:w-64">
                <label className="text-sm font-medium">Dataset</label>
                <Select value={selectedDataset} onValueChange={setSelectedDataset}>
                  <SelectTrigger className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="temperature">Temperature Survey</SelectItem>
                    <SelectItem value="species">Species Diversity</SelectItem>
                    <SelectItem value="monsoon">Monsoon Impact</SelectItem>
                    <SelectItem value="coastal">Coastal Study</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="lg:w-64">
                <label className="text-sm font-medium">Time Range</label>
                <Select defaultValue="6months">
                  <SelectTrigger className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1month">Last Month</SelectItem>
                    <SelectItem value="3months">Last 3 Months</SelectItem>
                    <SelectItem value="6months">Last 6 Months</SelectItem>
                    <SelectItem value="1year">Last Year</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="lg:w-64">
                <label className="text-sm font-medium">Region</label>
                <Select defaultValue="arabian">
                  <SelectTrigger className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="arabian">Arabian Sea</SelectItem>
                    <SelectItem value="bengal">Bay of Bengal</SelectItem>
                    <SelectItem value="kerala">Kerala Coast</SelectItem>
                    <SelectItem value="all">All Regions</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="charts" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="charts">Charts</TabsTrigger>
            <TabsTrigger value="maps">Maps</TabsTrigger>
            <TabsTrigger value="diversity">Diversity</TabsTrigger>
          </TabsList>

          <TabsContent value="charts" className="space-y-6">
            {/* Temperature vs Fish Abundance */}
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Thermometer className="h-5 w-5" />
                  <span>Temperature vs Fish Abundance</span>
                </CardTitle>
                <CardDescription>
                  Correlation between water temperature and fish abundance over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={temperatureData}>
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis dataKey="month" />
                      <YAxis yAxisId="left" orientation="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'white',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '6px'
                        }}
                      />
                      <Line 
                        yAxisId="left"
                        type="monotone" 
                        dataKey="temp" 
                        stroke="hsl(var(--destructive))" 
                        strokeWidth={3}
                        name="Temperature (°C)"
                      />
                      <Line 
                        yAxisId="right"
                        type="monotone" 
                        dataKey="abundance" 
                        stroke="hsl(var(--primary))" 
                        strokeWidth={3}
                        name="Fish Abundance"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Species Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="shadow-float">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Fish className="h-5 w-5" />
                    <span>Species Distribution</span>
                  </CardTitle>
                  <CardDescription>Fish species recorded in recent surveys</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={speciesData}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          dataKey="count"
                          label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                          {speciesData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-float">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="h-5 w-5" />
                    <span>Monthly Catches</span>
                  </CardTitle>
                  <CardDescription>Fish catch data by month</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={temperatureData}>
                        <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: 'white',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '6px'
                          }}
                        />
                        <Bar dataKey="abundance" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="maps" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Map className="h-5 w-5" />
                  <span>Sampling Stations Map</span>
                </CardTitle>
                <CardDescription>
                  Geographic distribution of sampling stations with environmental data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-96 rounded-lg overflow-hidden">
                  <MapContainer
                    center={[10.8505, 76.2711]}
                    zoom={7}
                    scrollWheelZoom={false}
                    className="h-full w-full"
                  >
                    <TileLayer
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    {samplingStations.map((station) => (
                      <CircleMarker
                        key={station.id}
                        center={station.position}
                        radius={10}
                        pathOptions={{
                          color: station.temp > 30 ? "#EF4444" : station.temp > 29 ? "#F59E0B" : "#10B981",
                          fillColor: station.temp > 30 ? "#EF4444" : station.temp > 29 ? "#F59E0B" : "#10B981",
                          fillOpacity: 0.8,
                          weight: 2
                        }}
                      >
                        <Popup>
                          <div className="p-2">
                            <h3 className="font-semibold">{station.name}</h3>
                            <p className="text-sm">Temperature: {station.temp}°C</p>
                            <p className="text-sm">Species Count: {station.species}</p>
                          </div>
                        </Popup>
                      </CircleMarker>
                    ))}
                  </MapContainer>
                </div>
                <div className="mt-4 flex items-center space-x-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span>Cold (&lt;29°C)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span>Moderate (29-30°C)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <span>Warm (&gt;30°C)</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="diversity" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Biodiversity Indices</span>
                </CardTitle>
                <CardDescription>
                  Species diversity and ecological health indicators
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {diversityData.map((item, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{item.parameter}</span>
                        <Badge variant="outline">
                          {item.value} / {item.max}
                        </Badge>
                      </div>
                      <div className="w-full bg-muted rounded-full h-3">
                        <div 
                          className="bg-gradient-ocean h-3 rounded-full transition-all duration-300"
                          style={{ width: `${(item.value / item.max) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="shadow-float">
                <CardHeader>
                  <CardTitle>Species Richness</CardTitle>
                  <CardDescription>Total unique species</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-primary">45</div>
                  <p className="text-sm text-muted-foreground">+3 from last survey</p>
                </CardContent>
              </Card>

              <Card className="shadow-float">
                <CardHeader>
                  <CardTitle>Endemic Species</CardTitle>
                  <CardDescription>Region-specific species</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-accent">12</div>
                  <p className="text-sm text-muted-foreground">26.7% of total</p>
                </CardContent>
              </Card>

              <Card className="shadow-float">
                <CardHeader>
                  <CardTitle>Threatened Species</CardTitle>
                  <CardDescription>Conservation status</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-destructive">3</div>
                  <p className="text-sm text-muted-foreground">Require monitoring</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Visualizations;