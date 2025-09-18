import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Brain, TrendingUp, Database, Search, BarChart3, Clock } from "lucide-react";
import { toast } from "sonner";
import { obisGeminiService } from '@/services/obisGeminiService';
import { Markdown } from '@/components/ui/markdown';

const Analytics = () => {
  const [analysisRunning, setAnalysisRunning] = useState(false);
  const [selectedSpecies, setSelectedSpecies] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('');
  const [obisData, setObisData] = useState<any>(null);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [statistics, setStatistics] = useState<any>(null);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const stats = await obisGeminiService.fetchOBISStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  };

  const runSpeciesAnalysis = async () => {
    if (!selectedSpecies.trim()) {
      toast.error('Please enter a species name');
      return;
    }

    setAnalysisRunning(true);
    try {
      const analysis = await obisGeminiService.searchSpeciesWithAI(selectedSpecies, undefined, 100);
      setAnalysisResults(analysis);
      setObisData(analysis.obis_data);
      toast.success('Species analysis completed successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to analyze species');
    } finally {
      setAnalysisRunning(false);
    }
  };

  const runRegionalAnalysis = async () => {
    if (!selectedRegion.trim()) {
      toast.error('Please enter region coordinates');
      return;
    }

    setAnalysisRunning(true);
    try {
      const analysis = await obisGeminiService.getMarineInsightsForRegion(selectedRegion, 'Selected Region');
      setAnalysisResults({ ai_analysis: analysis });
      toast.success('Regional analysis completed successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to analyze region');
    } finally {
      setAnalysisRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-depth p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">OBIS Marine Analytics</h1>
          <p className="text-muted-foreground">Real-time analysis of marine biodiversity data from OBIS with AI insights</p>
        </div>

        <Tabs defaultValue="species" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[500px]">
            <TabsTrigger value="species">Species Analysis</TabsTrigger>
            <TabsTrigger value="regional">Regional Analysis</TabsTrigger>
            <TabsTrigger value="statistics">OBIS Statistics</TabsTrigger>
          </TabsList>

          <TabsContent value="species" className="space-y-6">
            {/* Species Analysis Controls */}
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Search className="h-5 w-5" />
                  <span>Species Biodiversity Analysis</span>
                </CardTitle>
                <CardDescription>
                  Analyze species distribution, abundance, and ecological patterns using real OBIS data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Species Scientific Name</label>
                    <Input
                      className="mt-1"
                      placeholder="e.g., Thunnus albacares"
                      value={selectedSpecies}
                      onChange={(e) => setSelectedSpecies(e.target.value)}
                    />
                  </div>
                  <div className="flex items-end">
                    <Button 
                      onClick={runSpeciesAnalysis} 
                      disabled={analysisRunning}
                      className="bg-gradient-ocean w-full"
                    >
                      {analysisRunning ? (
                        <>
                          <Clock className="h-4 w-4 mr-2 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Database className="h-4 w-4 mr-2" />
                          Analyze Species
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Species Analysis Results */}
            {analysisResults && obisData && (
              <Card className="shadow-float">
                <CardHeader>
                  <CardTitle>Species Analysis Results</CardTitle>
                  <CardDescription>
                    AI-powered analysis of {selectedSpecies} based on {obisData.total} OBIS records
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Data Summary */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Card className="bg-blue-50">
                        <CardContent className="pt-6">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">
                              {obisData.total?.toLocaleString() || 0}
                            </div>
                            <div className="text-sm text-gray-600">Total Records</div>
                          </div>
                        </CardContent>
                      </Card>
                      <Card className="bg-green-50">
                        <CardContent className="pt-6">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {obisData.results?.length || 0}
                            </div>
                            <div className="text-sm text-gray-600">Retrieved Samples</div>
                          </div>
                        </CardContent>
                      </Card>
                      <Card className="bg-purple-50">
                        <CardContent className="pt-6">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">
                              {new Set(obisData.results?.map((r: any) => r.locality)).size || 0}
                            </div>
                            <div className="text-sm text-gray-600">Unique Locations</div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    {/* AI Analysis */}
                    <div>
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <Brain className="h-4 w-4" />
                        AI Analysis & Insights
                      </h4>
                      <Card className="bg-gray-50">
                        <CardContent className="pt-6">
                          <Markdown content={analysisResults.ai_analysis} className="text-sm" />
                        </CardContent>
                      </Card>
                    </div>

                    {/* Detailed Insights */}
                    {analysisResults.insights && (
                      <div>
                        <h4 className="font-medium mb-3">Detailed Ecological Insights</h4>
                        <div className="grid gap-4 md:grid-cols-2">
                          <Card>
                            <CardHeader>
                              <CardTitle className="text-base">Species Diversity</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <Markdown content={analysisResults.insights.species_diversity} className="text-sm" />
                            </CardContent>
                          </Card>
                          <Card>
                            <CardHeader>
                              <CardTitle className="text-base">Geographic Distribution</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <Markdown content={analysisResults.insights.geographic_distribution} className="text-sm" />
                            </CardContent>
                          </Card>
                          <Card>
                            <CardHeader>
                              <CardTitle className="text-base">Conservation Status</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <Markdown content={analysisResults.insights.conservation_status} className="text-sm" />
                            </CardContent>
                          </Card>
                          <Card>
                            <CardHeader>
                              <CardTitle className="text-base">Threats & Recommendations</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <Markdown content={analysisResults.insights.threats_and_recommendations} className="text-sm" />
                            </CardContent>
                          </Card>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="regional" className="space-y-6">
            {/* Regional Analysis Controls */}
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Regional Biodiversity Analysis</span>
                </CardTitle>
                <CardDescription>
                  Analyze marine biodiversity patterns in specific geographic regions
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Region Coordinates (WKT Format)</label>
                    <Input
                      className="mt-1"
                      placeholder="e.g., POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"
                      value={selectedRegion}
                      onChange={(e) => setSelectedRegion(e.target.value)}
                    />
                  </div>
                  <div className="flex items-end">
                    <Button 
                      onClick={runRegionalAnalysis} 
                      disabled={analysisRunning}
                      className="bg-gradient-ocean w-full"
                    >
                      {analysisRunning ? (
                        <>
                          <Clock className="h-4 w-4 mr-2 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <BarChart3 className="h-4 w-4 mr-2" />
                          Analyze Region
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Regional Analysis Results */}
            {analysisResults && analysisResults.ai_analysis && !obisData && (
              <Card className="shadow-float">
                <CardHeader>
                  <CardTitle>Regional Analysis Results</CardTitle>
                  <CardDescription>
                    AI-powered analysis of marine biodiversity in the selected region
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <Brain className="h-4 w-4" />
                        Regional Biodiversity Insights
                      </h4>
                      <Card className="bg-gray-50">
                        <CardContent className="pt-6">
                          <Markdown content={analysisResults.ai_analysis} className="text-sm" />
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="statistics" className="space-y-6">
            {/* Global OBIS Statistics */}
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Global OBIS Statistics</span>
                </CardTitle>
                <CardDescription>
                  Real-time statistics from the Ocean Biodiversity Information System
                </CardDescription>
              </CardHeader>
              <CardContent>
                {statistics ? (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {Object.entries(statistics).map(([key, value]) => (
                      <Card key={key} className="bg-gradient-to-br from-blue-50 to-indigo-50">
                        <CardContent className="pt-6">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">
                              {typeof value === 'number' ? value.toLocaleString() : String(value)}
                            </div>
                            <div className="text-sm text-gray-600 capitalize">
                              {key.replace(/_/g, ' ')}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Loading global statistics...</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Analytics;