import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Brain, TrendingUp, Zap, AlertCircle, CheckCircle, Clock } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Analytics = () => {
  const [analysisRunning, setAnalysisRunning] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState("correlation");
  const { toast } = useToast();

  const correlationResults = [
    { variables: "Temperature vs Species Richness", correlation: -0.72, significance: "p < 0.01", strength: "Strong Negative" },
    { variables: "Salinity vs Fish Abundance", correlation: 0.45, significance: "p < 0.05", strength: "Moderate Positive" },
    { variables: "pH vs Plankton Diversity", correlation: 0.38, significance: "p < 0.05", strength: "Weak Positive" },
    { variables: "Depth vs Species Count", correlation: -0.56, significance: "p < 0.01", strength: "Moderate Negative" },
  ];

  const aiInsights = [
    {
      id: 1,
      title: "Temperature-Biodiversity Relationship",
      insight: "Analysis reveals a strong negative correlation between water temperature and species richness. As temperatures rise above 30°C, biodiversity indices drop significantly, suggesting thermal stress on marine ecosystems.",
      confidence: 92,
      type: "correlation",
    },
    {
      id: 2,
      title: "Seasonal Migration Pattern",
      insight: "Machine learning models detect distinct seasonal patterns in fish abundance data. Peak abundances occur during monsoon periods (June-September), indicating strong correlation with seasonal environmental changes.",
      confidence: 87,
      type: "pattern",
    },
    {
      id: 3,
      title: "Coastal vs Deep-sea Diversity",
      insight: "Comparative analysis shows coastal regions have 40% higher species diversity but 25% lower individual abundance compared to deeper waters. This suggests different ecological strategies in varying depth zones.",
      confidence: 78,
      type: "comparison",
    },
  ];

  const analysisQueue = [
    { id: 1, name: "Monsoon Impact Analysis", status: "completed", progress: 100, duration: "2.3 min" },
    { id: 2, name: "Species Migration Tracking", status: "running", progress: 67, duration: "1.2 min remaining" },
    { id: 3, name: "Water Quality Correlation", status: "queued", progress: 0, duration: "Pending" },
    { id: 4, name: "Biodiversity Index Calculation", status: "queued", progress: 0, duration: "Pending" },
  ];

  const runAnalysis = () => {
    setAnalysisRunning(true);
    toast({
      title: "Analysis started",
      description: "Your correlation analysis is now running. Results will be available shortly.",
    });
    
    // Simulate analysis
    setTimeout(() => {
      setAnalysisRunning(false);
      toast({
        title: "Analysis complete",
        description: "Your correlation analysis has finished. Check the results below.",
      });
    }, 3000);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "running": return <Clock className="h-4 w-4 text-blue-600 animate-spin" />;
      case "queued": return <Clock className="h-4 w-4 text-gray-400" />;
      default: return <AlertCircle className="h-4 w-4 text-red-600" />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return "text-green-600";
    if (confidence >= 70) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="min-h-screen bg-gradient-depth p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Analytics Engine</h1>
          <p className="text-muted-foreground">AI-powered analysis and insights for marine research data</p>
        </div>

        <Tabs defaultValue="correlations" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="correlations">Correlations</TabsTrigger>
            <TabsTrigger value="insights">AI Insights</TabsTrigger>
            <TabsTrigger value="queue">Analysis Queue</TabsTrigger>
          </TabsList>

          <TabsContent value="correlations" className="space-y-6">
            {/* Analysis Controls */}
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5" />
                  <span>Correlation Analysis</span>
                </CardTitle>
                <CardDescription>
                  Discover relationships between environmental factors and marine biodiversity
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm font-medium">Primary Variable</label>
                    <Select defaultValue="temperature">
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="temperature">Water Temperature</SelectItem>
                        <SelectItem value="salinity">Salinity</SelectItem>
                        <SelectItem value="ph">pH Level</SelectItem>
                        <SelectItem value="depth">Depth</SelectItem>
                        <SelectItem value="oxygen">Dissolved Oxygen</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Secondary Variable</label>
                    <Select defaultValue="species">
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="species">Species Richness</SelectItem>
                        <SelectItem value="abundance">Fish Abundance</SelectItem>
                        <SelectItem value="diversity">Shannon Diversity</SelectItem>
                        <SelectItem value="biomass">Total Biomass</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Method</label>
                    <Select defaultValue="pearson">
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pearson">Pearson Correlation</SelectItem>
                        <SelectItem value="spearman">Spearman Rank</SelectItem>
                        <SelectItem value="kendall">Kendall Tau</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <Button 
                  onClick={runAnalysis} 
                  disabled={analysisRunning}
                  className="bg-gradient-ocean"
                >
                  {analysisRunning ? (
                    <>
                      <Clock className="h-4 w-4 mr-2 animate-spin" />
                      Running Analysis...
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4 mr-2" />
                      Run Correlation Analysis
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Results */}
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle>Correlation Results</CardTitle>
                <CardDescription>Statistical relationships between variables</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {correlationResults.map((result, index) => (
                    <div key={index} className="p-4 border border-border rounded-lg hover:shadow-float transition-shadow">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium">{result.variables}</h4>
                        <Badge variant="outline">{result.strength}</Badge>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Correlation:</span>
                          <span className={`ml-2 font-mono font-bold ${result.correlation < 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {result.correlation.toFixed(2)}
                          </span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Significance:</span>
                          <span className="ml-2 font-medium">{result.significance}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Strength:</span>
                          <span className="ml-2 font-medium">{result.strength}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="insights" className="space-y-6">
            <div className="grid gap-6">
              {aiInsights.map((insight) => (
                <Card key={insight.id} className="shadow-float">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="flex items-center space-x-2">
                          <Brain className="h-5 w-5" />
                          <span>{insight.title}</span>
                        </CardTitle>
                        <CardDescription>AI-generated insight from data analysis</CardDescription>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${getConfidenceColor(insight.confidence)}`}>
                          {insight.confidence}%
                        </div>
                        <div className="text-xs text-muted-foreground">Confidence</div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <p className="text-foreground leading-relaxed">{insight.insight}</p>
                      <div className="flex items-center justify-between">
                        <Badge variant="secondary">{insight.type}</Badge>
                        <div className="text-sm text-muted-foreground">
                          Generated using machine learning algorithms
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card className="shadow-float">
              <CardHeader>
                <CardTitle>Custom Analysis Request</CardTitle>
                <CardDescription>Describe what you'd like to analyze in natural language</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea 
                  placeholder="e.g., 'Find the relationship between monsoon rainfall and fish migration patterns in the Arabian Sea during 2024'"
                  className="min-h-[100px]"
                />
                <Button className="bg-gradient-coral">
                  <Brain className="h-4 w-4 mr-2" />
                  Generate AI Analysis
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="queue" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Analysis Queue</span>
                </CardTitle>
                <CardDescription>Monitor running and scheduled analysis tasks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysisQueue.map((item) => (
                    <div key={item.id} className="p-4 border border-border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(item.status)}
                          <div>
                            <h4 className="font-medium">{item.name}</h4>
                            <p className="text-sm text-muted-foreground">{item.duration}</p>
                          </div>
                        </div>
                        <Badge 
                          variant={item.status === "completed" ? "default" : "secondary"}
                          className={item.status === "completed" ? "bg-green-100 text-green-800" : ""}
                        >
                          {item.status}
                        </Badge>
                      </div>
                      {item.status !== "queued" && (
                        <Progress value={item.progress} className="h-2" />
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="shadow-float">
                <CardHeader>
                  <CardTitle>Queue Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary">4</div>
                  <p className="text-sm text-muted-foreground">Total jobs</p>
                </CardContent>
              </Card>

              <Card className="shadow-float">
                <CardHeader>
                  <CardTitle>Processing Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-accent">1.2 min</div>
                  <p className="text-sm text-muted-foreground">Average duration</p>
                </CardContent>
              </Card>

              <Card className="shadow-float">
                <CardHeader>
                  <CardTitle>Success Rate</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">98.5%</div>
                  <p className="text-sm text-muted-foreground">Last 30 days</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Analytics;