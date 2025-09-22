import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Brain, 
  MessageSquare, 
  Lightbulb, 
  Loader2,
  Database,
  Search,
  Globe,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import { geminiApi } from '@/services/geminiApi';
import { obisGeminiService } from '@/services/obisGeminiService';
import { Markdown } from '@/components/ui/markdown';

interface AIResponse {
  status: string;
  content?: string;
  error?: string;
}

const AIIntegration: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [chatQuestion, setChatQuestion] = useState('');
  const [chatResponse, setChatResponse] = useState<AIResponse | null>(null);
  const [analysisData, setAnalysisData] = useState('');
  const [analysisResponse, setAnalysisResponse] = useState<AIResponse | null>(null);
  const [quickInsights, setQuickInsights] = useState<AIResponse | null>(null);
  const [speciesSearch, setSpeciesSearch] = useState('');
  const [speciesAnalysis, setSpeciesAnalysis] = useState<any>(null);
  const [datasetId, setDatasetId] = useState('');
  const [datasetAnalysis, setDatasetAnalysis] = useState<any>(null);
  const [regionGeometry, setRegionGeometry] = useState('');
  const [regionAnalysis, setRegionAnalysis] = useState<any>(null);

  const handleChatSubmit = async () => {
    if (!chatQuestion.trim()) {
      toast.error('Please enter a question');
      return;
    }

    setLoading(true);
    try {
      const content = await geminiApi.chatAboutMarine(chatQuestion);
      setChatResponse({ status: 'success', content });
      toast.success('AI response generated successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to get AI response');
      setChatResponse({ status: 'error', error: error.message || 'Unknown error' });
    } finally {
      setLoading(false);
    }
  };

  const handleAnalysisSubmit = async () => {
    if (!analysisData.trim()) {
      toast.error('Please enter data to analyze');
      return;
    }

    setLoading(true);
    try {
      let parsedData;
      try {
        parsedData = JSON.parse(analysisData);
      } catch {
        // If not JSON, treat as text description
        parsedData = { description: analysisData, type: 'text_description' };
      }

      const content = await geminiApi.analyzeMarineData(parsedData);
      setAnalysisResponse({ status: 'success', content });
      toast.success('Analysis completed successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to analyze data');
      setAnalysisResponse({ status: 'error', error: error.message || 'Unknown error' });
    } finally {
      setLoading(false);
    }
  };

  const getQuickInsights = async () => {
    setLoading(true);
    try {
      const content = await geminiApi.getMarineInsights();
      setQuickInsights({ status: 'success', content });
      toast.success('Quick insights generated');
    } catch (error: any) {
      toast.error(error.message || 'Failed to get insights');
      setQuickInsights({ status: 'error', error: error.message || 'Unknown error' });
    } finally {
      setLoading(false);
    }
  };

  const searchSpeciesWithAI = async () => {
    if (!speciesSearch.trim()) {
      toast.error('Please enter a species name');
      return;
    }

    setLoading(true);
    try {
      const analysis = await obisGeminiService.searchSpeciesWithAI(speciesSearch, undefined, 50);
      setSpeciesAnalysis(analysis);
      toast.success('Species analysis completed');
    } catch (error: any) {
      toast.error(error.message || 'Failed to analyze species');
      setSpeciesAnalysis({ error: error.message || 'Unknown error' });
    } finally {
      setLoading(false);
    }
  };

  const analyzeDatasetWithAI = async () => {
    if (!datasetId.trim()) {
      toast.error('Please enter a dataset ID');
      return;
    }

    setLoading(true);
    try {
      const analysis = await obisGeminiService.analyzeDatasetWithAI(datasetId);
      setDatasetAnalysis(analysis);
      toast.success('Dataset analysis completed');
    } catch (error: any) {
      toast.error(error.message || 'Failed to analyze dataset');
      setDatasetAnalysis({ error: error.message || 'Unknown error' });
    } finally {
      setLoading(false);
    }
  };

  const analyzeRegionWithAI = async () => {
    if (!regionGeometry.trim()) {
      toast.error('Please enter region coordinates or WKT geometry');
      return;
    }

    setLoading(true);
    try {
      const analysis = await obisGeminiService.getMarineInsightsForRegion(regionGeometry, 'User-specified region');
      setRegionAnalysis({ content: analysis, status: 'success' });
      toast.success('Regional analysis completed');
    } catch (error: any) {
      toast.error(error.message || 'Failed to analyze region');
      setRegionAnalysis({ error: error.message || 'Unknown error', status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Brain className="h-8 w-8 text-blue-600" />
          AI-Powered Marine Analysis
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Leverage Google Gemini AI to analyze marine biodiversity data, generate insights, 
          and get expert recommendations for conservation efforts.
        </p>
      </div>

      <div className="flex justify-center">
        <Button onClick={getQuickInsights} disabled={loading} variant="outline">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
          Test AI Service
        </Button>
      </div>

      <Tabs defaultValue="chat" className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="chat">AI Chat</TabsTrigger>
          <TabsTrigger value="analysis">Data Analysis</TabsTrigger>
          <TabsTrigger value="insights">Quick Insights</TabsTrigger>
          <TabsTrigger value="species">Species + AI</TabsTrigger>
          <TabsTrigger value="dataset">Dataset + AI</TabsTrigger>
          <TabsTrigger value="region">Region + AI</TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Marine Biology AI Chat
              </CardTitle>
              <CardDescription>
                Ask questions about marine ecosystems, biodiversity, and conservation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Your Question:</label>
                <Textarea
                  placeholder="e.g., What are the main threats to coral reef ecosystems? How does ocean acidification affect marine biodiversity?"
                  value={chatQuestion}
                  onChange={(e) => setChatQuestion(e.target.value)}
                  rows={3}
                />
              </div>
              <Button onClick={handleChatSubmit} disabled={loading} className="w-full">
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <MessageSquare className="h-4 w-4 mr-2" />}
                Ask AI
              </Button>
              
              {chatResponse && (
                <Card className="bg-gray-50">
                  <CardContent className="pt-6">
                    {chatResponse.status === 'success' ? (
                      <div className="space-y-3">
                        <Badge variant="secondary">AI Response</Badge>
                        <Markdown content={chatResponse.content} className="text-sm" />
                      </div>
                    ) : (
                      <div className="text-red-600">
                        <strong>Error:</strong> {chatResponse.error}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Marine Data Analysis
              </CardTitle>
              <CardDescription>
                Analyze marine biodiversity data and get AI-powered insights
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Data to Analyze:</label>
                <Textarea
                  placeholder='Enter JSON data or description, e.g., {"species_count": 25, "location": "Pacific Ocean", "depth_range": "0-200m"}'
                  value={analysisData}
                  onChange={(e) => setAnalysisData(e.target.value)}
                  rows={5}
                />
              </div>
              <Button onClick={handleAnalysisSubmit} disabled={loading} className="w-full">
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Brain className="h-4 w-4 mr-2" />}
                Analyze Data
              </Button>
              
              {analysisResponse && (
                <Card className="bg-gray-50">
                  <CardContent className="pt-6">
                    {analysisResponse.status === 'success' ? (
                      <div className="space-y-4">
                        <Badge variant="secondary">Analysis Complete</Badge>
                        <div className="space-y-3">
                          <div>
                            <h4 className="font-medium mb-2">Analysis:</h4>
                            <Markdown content={analysisResponse.content} className="text-sm" />
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-red-600">
                        <strong>Error:</strong> {analysisResponse.error}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5" />
                Quick Marine Insights
              </CardTitle>
              <CardDescription>
                Get instant AI insights about current marine biodiversity trends
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button onClick={getQuickInsights} disabled={loading} className="w-full">
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Lightbulb className="h-4 w-4 mr-2" />}
                Generate Quick Insights
              </Button>
              
              {quickInsights && (
                <Card className="bg-gray-50">
                  <CardContent className="pt-6">
                    {quickInsights.status === 'success' ? (
                      <div className="space-y-4">
                        <Badge variant="secondary">AI Insights</Badge>
                        <Markdown content={quickInsights.content} className="text-sm" />
                      </div>
                    ) : (
                      <div className="text-red-600">
                        <strong>Error:</strong> {quickInsights.error}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="species" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                OBIS Species Analysis with AI
              </CardTitle>
              <CardDescription>
                Search for species in OBIS database and get AI-powered ecological analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Species Scientific Name:</label>
                <Input
                  placeholder="e.g., Thunnus albacares (Yellowfin Tuna)"
                  value={speciesSearch}
                  onChange={(e) => setSpeciesSearch(e.target.value)}
                />
              </div>
              <Button onClick={searchSpeciesWithAI} disabled={loading} className="w-full">
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Search className="h-4 w-4 mr-2" />}
                Search & Analyze Species
              </Button>
              
              {speciesAnalysis && (
                <Card className="bg-gray-50">
                  <CardContent className="pt-6">
                    {speciesAnalysis.error ? (
                      <div className="text-red-600">
                        <strong>Error:</strong> {speciesAnalysis.error}
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <Badge variant="secondary">OBIS + AI Analysis Complete</Badge>
                        
                        <div>
                          <h4 className="font-medium mb-2">OBIS Data Summary:</h4>
                          <p className="text-sm text-gray-600">
                            Found {speciesAnalysis.obis_data?.total || 0} records in OBIS database
                          </p>
                        </div>
                        
                        <div>
                          <h4 className="font-medium mb-2">AI Analysis:</h4>
                          <Markdown content={speciesAnalysis.ai_analysis} className="text-sm" />
                        </div>
                        
                        <div>
                          <h4 className="font-medium mb-2">OBIS Data:</h4>
                          <pre className="text-sm whitespace-pre-wrap">{JSON.stringify(speciesAnalysis.obis_data, null, 2)}</pre>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dataset" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                OBIS Dataset Analysis with AI
              </CardTitle>
              <CardDescription>
                Analyze OBIS dataset and get AI-powered insights
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Dataset ID:</label>
                <Input
                  placeholder="e.g., 12345"
                  value={datasetId}
                  onChange={(e) => setDatasetId(e.target.value)}
                />
              </div>
              <Button onClick={analyzeDatasetWithAI} disabled={loading} className="w-full">
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Database className="h-4 w-4 mr-2" />}
                Analyze Dataset
              </Button>
              
              {datasetAnalysis && (
                <Card className="bg-gray-50">
                  <CardContent className="pt-6">
                    {datasetAnalysis.error ? (
                      <div className="text-red-600">
                        <strong>Error:</strong> {datasetAnalysis.error}
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <Badge variant="secondary">OBIS + AI Analysis Complete</Badge>
                        
                        <div>
                          <h4 className="font-medium mb-2">OBIS Data Summary:</h4>
                          <p className="text-sm text-gray-600">
                            Found {datasetAnalysis.obis_data?.total || 0} records in OBIS database
                          </p>
                        </div>
                        
                        <div>
                          <h4 className="font-medium mb-2">AI Analysis:</h4>
                          <Markdown content={datasetAnalysis.ai_analysis} className="text-sm" />
                        </div>
                        
                        <div>
                          <h4 className="font-medium mb-2">OBIS Data:</h4>
                          <pre className="text-sm whitespace-pre-wrap">{JSON.stringify(datasetAnalysis.obis_data, null, 2)}</pre>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="region" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                OBIS Region Analysis with AI
              </CardTitle>
              <CardDescription>
                Analyze marine biodiversity in a specific region and get AI-powered insights
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Region Coordinates or WKT Geometry:</label>
                <Textarea
                  placeholder="e.g., POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"
                  value={regionGeometry}
                  onChange={(e) => setRegionGeometry(e.target.value)}
                  rows={3}
                />
              </div>
              <Button onClick={analyzeRegionWithAI} disabled={loading} className="w-full">
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Globe className="h-4 w-4 mr-2" />}
                Analyze Region
              </Button>
              
              {regionAnalysis && (
                <Card className="bg-gray-50">
                  <CardContent className="pt-6">
                    {regionAnalysis.status === 'success' ? (
                      <div className="space-y-4">
                        <Badge variant="secondary">OBIS + AI Analysis Complete</Badge>
                        
                        <div>
                          <h4 className="font-medium mb-2">OBIS Data Summary:</h4>
                          <p className="text-sm text-gray-600">
                            Found {regionAnalysis.content?.total || 0} records in OBIS database
                          </p>
                        </div>
                        
                        <div>
                          <h4 className="font-medium mb-2">AI Analysis:</h4>
                          <Markdown content={regionAnalysis.content?.ai_analysis} className="text-sm" />
                        </div>
                        
                        <div>
                          <h4 className="font-medium mb-2">OBIS Data:</h4>
                          <pre className="text-sm whitespace-pre-wrap">{JSON.stringify(regionAnalysis.content?.obis_data, null, 2)}</pre>
                        </div>
                      </div>
                    ) : (
                      <div className="text-red-600">
                        <strong>Error:</strong> {regionAnalysis.error}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>

      </Tabs>
    </div>
  );
};

export default AIIntegration;