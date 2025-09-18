import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Brain, 
  MessageSquare, 
  Lightbulb, 
  Loader2,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import { geminiApi } from '@/services/geminiApi';

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

  const testAIService = async () => {
    setLoading(true);
    try {
      const content = await geminiApi.generateContent('Hello, this is a test. Please respond with a simple greeting.');
      toast.success('AI service is working: ' + content.substring(0, 50) + '...');
    } catch (error: any) {
      toast.error(error.message || 'AI service test failed');
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
        <Button onClick={testAIService} disabled={loading} variant="outline">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
          Test AI Service
        </Button>
      </div>

      <Tabs defaultValue="chat" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="chat">AI Chat</TabsTrigger>
          <TabsTrigger value="analysis">Data Analysis</TabsTrigger>
          <TabsTrigger value="insights">Quick Insights</TabsTrigger>
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
                  placeholder="e.g., What are the main threats to coral reef ecosystems?"
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
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{chatResponse.content}</p>
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
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{analysisResponse.content}</p>
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
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{quickInsights.content}</p>
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
      </Tabs>
    </div>
  );
};

export default AIIntegration;