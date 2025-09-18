import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ArrowUpRight, Database, Map, BarChart3, Fish, Waves, Thermometer, TreePine } from "lucide-react";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { healthApi, dataIntegrationApi, biodiversityApi } from "@/services/marineApi";
import { useToast } from "@/hooks/use-toast";

const Dashboard = () => {
  const { toast } = useToast();
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Check system status using direct OBIS API
  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        setLoading(true);
        
        // Test direct OBIS API connection instead of backend
        const obisResponse = await fetch('https://api.obis.org/v3/statistics');
        
        if (obisResponse.ok) {
          toast({
            title: "System Connected",
            description: "OBIS API is accessible - Marine data available",
          });
          
          // Use OBIS statistics as system status
          const obisStats = await obisResponse.json();
          setSystemStatus({
            status: "connected",
            obis_connection: "active",
            last_update: new Date().toISOString(),
            records: obisStats.records || "Available"
          });
        } else {
          throw new Error('OBIS API not accessible');
        }
      } catch (error) {
        console.error('System status check failed:', error);
        toast({
          title: "Limited Connection",
          description: "Using offline mode - Some features may be limited",
          variant: "destructive",
        });
        // Set demo status
        setSystemStatus({
          status: "offline",
          obis_connection: "unavailable",
          last_update: new Date().toISOString()
        });
      } finally {
        setLoading(false);
      }
    };

    checkSystemStatus();
  }, [toast]);
  const stats = [
    { title: "Active Datasets", value: "47", change: "+12%", icon: Database, color: "bg-gradient-ocean" },
    { title: "Species Recorded", value: "1,234", change: "+5%", icon: Fish, color: "bg-gradient-coral" },
    { title: "Temperature Readings", value: "89.2K", change: "+8%", icon: Thermometer, color: "bg-accent" },
    { title: "Sampling Stations", value: "156", change: "+2%", icon: Map, color: "bg-primary" },
  ];

  const recentActivity = [
    { id: 1, action: "New dataset uploaded", dataset: "Arabian Sea Temperature Survey", time: "2 hours ago", type: "upload" },
    { id: 2, action: "Analysis completed", dataset: "Coastal Fish Diversity", time: "4 hours ago", type: "analysis" },
    { id: 3, action: "Visualization created", dataset: "Monsoon Impact Study", time: "6 hours ago", type: "visualization" },
    { id: 4, action: "New species identified", dataset: "Deep Sea Exploration", time: "1 day ago", type: "discovery" },
  ];

  return (
    <div className="min-h-screen bg-gradient-depth p-6">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-ocean p-8 text-primary-foreground shadow-ocean">
          <div className="relative z-10">
            <div className="flex items-center space-x-3 mb-4">
              <Waves className="h-8 w-8 animate-wave" />
              <h1 className="text-3xl font-bold">Centre for Marine Living Resources and Ecology</h1>
            </div>
            <p className="text-xl text-primary-foreground/90 mb-6 max-w-2xl">
              Sustainable Oceans through Integrated Data
            </p>
            <div className="flex flex-wrap gap-3">
              <Button variant="secondary" size="lg" asChild>
                <Link to="/datasets">
                  <Database className="h-4 w-4 mr-2" />
                  Explore Datasets
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="bg-white/10 border-white/20 text-white hover:bg-white/20" asChild>
                <Link to="/visualizations">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  View Analytics
                </Link>
              </Button>
            </div>
          </div>
          <div className="absolute top-4 right-4 opacity-20">
            <div className="grid grid-cols-3 gap-2">
              <Fish className="h-12 w-12" />
              <Waves className="h-12 w-12" />
              <TreePine className="h-12 w-12" />
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={index} className="border-0 shadow-float hover:shadow-ocean transition-all duration-300 animate-fade-up" style={{ animationDelay: `${index * 100}ms` }}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
                  <div className={`p-2 rounded-lg ${stat.color}`}>
                    <Icon className="h-4 w-4 text-white" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-emerald-600">{stat.change}</span> from last month
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <Card className="lg:col-span-1 shadow-float">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <div className="p-1 bg-gradient-coral rounded-lg">
                <ArrowUpRight className="h-4 w-4 text-white" />
              </div>
              <span>Quick Actions</span>
            </CardTitle>
            <CardDescription>Common tasks and tools</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start" asChild>
              <Link to="/datasets">
                <Database className="h-4 w-4 mr-2" />
                Upload New Dataset
              </Link>
            </Button>
            <Button variant="outline" className="w-full justify-start" asChild>
              <Link to="/tools">
                <Fish className="h-4 w-4 mr-2" />
                Species Identification
              </Link>
            </Button>
            <Button variant="outline" className="w-full justify-start" asChild>
              <Link to="/analytics">
                <BarChart3 className="h-4 w-4 mr-2" />
                Run Analysis
              </Link>
            </Button>
            <Button variant="outline" className="w-full justify-start" asChild>
              <Link to="/visualizations">
                <Map className="h-4 w-4 mr-2" />
                Create Visualization
              </Link>
            </Button>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="lg:col-span-2 shadow-float">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest updates across all projects</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-gradient-ocean rounded-lg">
                      <Database className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <p className="font-medium">{activity.action}</p>
                      <p className="text-sm text-muted-foreground">{activity.dataset}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="secondary" className="mb-1">
                      {activity.type}
                    </Badge>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* System Status */}
        <Card className="lg:col-span-1 shadow-float">
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>Platform health overview</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {loading ? (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="text-sm text-muted-foreground mt-2">Checking system status...</p>
              </div>
            ) : (
              <>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Storage Usage</span>
                    <span>{systemStatus?.pipeline_status?.system_health ? '45%' : '67%'}</span>
                  </div>
                  <Progress value={systemStatus?.pipeline_status?.system_health ? 45 : 67} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Processing Queue</span>
                    <span>23%</span>
                  </div>
                  <Progress value={23} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>API Performance</span>
                    <span>{systemStatus ? '98%' : '94%'}</span>
                  </div>
                  <Progress value={systemStatus ? 98 : 94} className="h-2" />
                </div>
                {systemStatus && (
                  <div className="text-xs text-muted-foreground mt-2">
                    <p>Active Connections: {systemStatus.pipeline_status?.system_health?.active_connections || 0}</p>
                    <p>CPU Usage: {((systemStatus.pipeline_status?.system_health?.cpu_usage || 0) * 100).toFixed(1)}%</p>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Data Quality Metrics */}
        <Card className="lg:col-span-2 shadow-float">
          <CardHeader>
            <CardTitle>Data Quality Metrics</CardTitle>
            <CardDescription>Overview of dataset completeness and validation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 rounded-lg bg-emerald-50 border border-emerald-200">
                <div className="text-2xl font-bold text-emerald-600">98.5%</div>
                <div className="text-sm text-emerald-800">Validated</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-blue-50 border border-blue-200">
                <div className="text-2xl font-bold text-blue-600">45</div>
                <div className="text-sm text-blue-800">Species Types</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-purple-50 border border-purple-200">
                <div className="text-2xl font-bold text-purple-600">12.3TB</div>
                <div className="text-sm text-purple-800">Total Data</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-orange-50 border border-orange-200">
                <div className="text-2xl font-bold text-orange-600">156</div>
                <div className="text-sm text-orange-800">Locations</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;