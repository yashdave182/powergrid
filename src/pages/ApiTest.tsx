import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import { biodiversityApi, oceanographyApi, healthApi } from "@/services/marineApi";
import { Loader2, Search, TestTube, Waves } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const ApiTest = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [coordinates, setCoordinates] = useState({ lat: "12.9716", lng: "77.5946" });

  const testHealthAPI = async () => {
    setLoading(true);
    try {
      const response = await healthApi.checkHealth();
      setResults(response);
      
      if (response.error) {
        toast({
          title: "Health Check Failed",
          description: response.error,
          variant: "destructive",
        });
      } else {
        toast({
          title: "Health Check Successful",
          description: "Backend is running properly",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to connect to backend",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const testSpeciesSearch = async () => {
    if (!searchTerm.trim()) {
      toast({
        title: "Input Required",
        description: "Please enter a species name",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await biodiversityApi.searchSpecies({
        scientific_name: searchTerm,
        data_source: 'both',
        limit: 10
      });
      setResults(response);
      
      if (response.error) {
        toast({
          title: "Species Search Failed",
          description: response.error,
          variant: "destructive",
        });
      } else {
        toast({
          title: "Species Search Successful",
          description: `Found data from ${response.data?.total_sources || 0} sources`,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Species search failed",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const testOceanographyAPI = async () => {
    setLoading(true);
    try {
      const response = await oceanographyApi.getTemperatureProfiles(
        parseFloat(coordinates.lat),
        parseFloat(coordinates.lng)
      );
      setResults(response);
      
      if (response.error) {
        toast({
          title: "Oceanography API Failed",
          description: response.error,
          variant: "destructive",
        });
      } else {
        toast({
          title: "Oceanography API Successful",
          description: "Temperature data retrieved",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Oceanography API test failed",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-depth p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">API Testing</h1>
          <p className="text-muted-foreground">Test connection to Marine Data Platform backend</p>
        </div>

        <Tabs defaultValue="health" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="health">Health</TabsTrigger>
            <TabsTrigger value="species">Species</TabsTrigger>
            <TabsTrigger value="ocean">Ocean Data</TabsTrigger>
          </TabsList>

          <TabsContent value="health" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TestTube className="h-5 w-5" />
                  <span>Backend Health Check</span>
                </CardTitle>
                <CardDescription>
                  Test if the backend API is running and accessible
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={testHealthAPI} disabled={loading} className="w-full">
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Test Health API
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="species" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Search className="h-5 w-5" />
                  <span>Species Search API</span>
                </CardTitle>
                <CardDescription>
                  Search for marine species using OBIS and GBIF databases
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="species-search">Species Name</Label>
                  <Input
                    id="species-search"
                    placeholder="e.g., Thunnus albacares (Yellowfin Tuna)"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <Button onClick={testSpeciesSearch} disabled={loading} className="w-full">
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Search Species
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ocean" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Waves className="h-5 w-5" />
                  <span>Oceanographic Data API</span>
                </CardTitle>
                <CardDescription>
                  Get temperature profiles for specified coordinates
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="latitude">Latitude</Label>
                    <Input
                      id="latitude"
                      placeholder="12.9716"
                      value={coordinates.lat}
                      onChange={(e) => setCoordinates(prev => ({ ...prev, lat: e.target.value }))}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="longitude">Longitude</Label>
                    <Input
                      id="longitude"
                      placeholder="77.5946"
                      value={coordinates.lng}
                      onChange={(e) => setCoordinates(prev => ({ ...prev, lng: e.target.value }))}
                      className="mt-1"
                    />
                  </div>
                </div>
                <Button onClick={testOceanographyAPI} disabled={loading} className="w-full">
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Get Temperature Data
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Results Display */}
        {results && (
          <Card className="mt-6 shadow-float">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>API Response</span>
                <Badge variant={results.error ? "destructive" : "default"}>
                  Status: {results.status}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm max-h-96">
                {JSON.stringify(results, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ApiTest;