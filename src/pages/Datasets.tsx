import React, { useState, useEffect } from 'react';
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Database, 
  Search, 
  Loader2, 
  FileText,
  BarChart3,
  ExternalLink,
  Activity
} from 'lucide-react';
import { toast } from 'sonner';
import { obisGeminiService, obisDataService } from '@/services/obisGeminiService';
import { Markdown } from '@/components/ui/markdown';

interface OBISDataset {
  id: string;
  title: string;
  description?: string;
  abstract?: string;
  citation?: string;
  license?: string;
  records?: number;
  url?: string;
  extent?: {
    spatial?: string;
    temporal?: string;
  };
}

const Datasets: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [datasets, setDatasets] = useState<OBISDataset[]>([]);
  const [totalDatasets, setTotalDatasets] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDataset, setSelectedDataset] = useState<OBISDataset | null>(null);
  const [datasetAnalysis, setDatasetAnalysis] = useState<any>(null);
  const [statistics, setStatistics] = useState<any>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const datasetsPerPage = 10;

  useEffect(() => {
    loadDatasets();
    loadStatistics();
  }, [currentPage]);

  const loadDatasets = async () => {
    setLoading(true);
    setLoadingProgress(0);
    setLoadingMessage('Connecting to OBIS API...');
    
    try {
      // Simulate progress updates
      setLoadingProgress(20);
      setLoadingMessage('Requesting dataset list from OBIS...');
      
      const result = await obisGeminiService.fetchOBISDatasets(datasetsPerPage, currentPage * datasetsPerPage);
      
      setLoadingProgress(60);
      setLoadingMessage('Processing dataset information...');
      
      // Add a small delay to show progress
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setLoadingProgress(80);
      setLoadingMessage('Organizing results...');
      
      setDatasets(result.datasets || []);
      setTotalDatasets(result.total || 0);
      
      setLoadingProgress(100);
      setLoadingMessage('Complete!');
      
      toast.success(`Loaded ${result.datasets?.length || 0} OBIS datasets`);
    } catch (error: any) {
      setLoadingProgress(0);
      setLoadingMessage('Failed to load datasets');
      toast.error(error.message || 'Failed to load datasets');
      console.error('Error loading datasets:', error);
    } finally {
      setTimeout(() => {
        setLoading(false);
        setLoadingProgress(0);
        setLoadingMessage('');
      }, 1000);
    }
  };

  const loadStatistics = async () => {
    setLoadingProgress(10);
    setLoadingMessage('Loading OBIS statistics...');
    try {
      const stats = await obisGeminiService.fetchOBISStatistics();
      setStatistics(stats);
      setLoadingProgress(100);
      setLoadingMessage('Statistics loaded!');
    } catch (error: any) {
      console.error('Error loading statistics:', error);
      setLoadingMessage('Statistics unavailable');
    }
  };

  const analyzeDataset = async (dataset: OBISDataset) => {
    setSelectedDataset(dataset);
    setLoading(true);
    setLoadingProgress(0);
    setLoadingMessage('Preparing dataset analysis...');
    
    try {
      setLoadingProgress(25);
      setLoadingMessage('Sending dataset to AI for analysis...');
      
      const analysis = await obisGeminiService.analyzeDatasetWithAI(dataset.id);
      
      setLoadingProgress(75);
      setLoadingMessage('Processing AI insights...');
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setDatasetAnalysis(analysis);
      setLoadingProgress(100);
      setLoadingMessage('Analysis complete!');
      
      toast.success('Dataset analysis completed');
    } catch (error: any) {
      setLoadingProgress(0);
      setLoadingMessage('Analysis failed');
      toast.error(error.message || 'Failed to analyze dataset');
      setDatasetAnalysis({ error: error.message || 'Unknown error' });
    } finally {
      setTimeout(() => {
        setLoading(false);
        setLoadingProgress(0);
        setLoadingMessage('');
      }, 1000);
    }
  };

  const filteredDatasets = datasets.filter(dataset =>
    (dataset.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (dataset.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (dataset.abstract || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(totalDatasets / datasetsPerPage);

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Database className="h-8 w-8 text-blue-600" />
          OBIS Marine Datasets
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Explore real marine biodiversity datasets from OBIS with AI-powered analysis.
        </p>
      </div>

      <Tabs defaultValue="browse" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="browse">Browse Datasets</TabsTrigger>
          <TabsTrigger value="analysis">Dataset Analysis</TabsTrigger>
          <TabsTrigger value="statistics">OBIS Statistics</TabsTrigger>
        </TabsList>

        <TabsContent value="browse" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                OBIS Dataset Browser
              </CardTitle>
              <CardDescription>
                Browse and search through real marine biodiversity datasets from OBIS
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search datasets by title or description..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <Button onClick={loadDatasets} disabled={loading}>
                  {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Search className="h-4 w-4 mr-2" />}
                  Refresh
                </Button>
              </div>

              <div className="text-sm text-gray-600">
                Showing {filteredDatasets.length} of {totalDatasets} datasets from OBIS
              </div>

              {loading ? (
                <Card className="p-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-center">
                      <Loader2 className="h-8 w-8 animate-spin mr-3 text-blue-600" />
                      <div className="text-center">
                        <div className="font-medium">{loadingMessage}</div>
                        <div className="text-sm text-gray-500">{loadingProgress}% complete</div>
                      </div>
                    </div>
                    <Progress value={loadingProgress} className="w-full" />
                    <div className="text-xs text-center text-gray-400">
                      Fetching real-time data from OBIS Marine Database...
                    </div>
                  </div>
                </Card>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {filteredDatasets.map((dataset) => (
                    <Card key={dataset.id} className="hover:shadow-md transition-shadow">
                      <CardHeader>
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <CardTitle className="text-base">{dataset.title}</CardTitle>
                            <div className="flex gap-2 mt-2">
                              <Badge variant="outline">ID: {dataset.id}</Badge>
                              {dataset.records && (
                                <Badge variant="secondary">{dataset.records.toLocaleString()} records</Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="text-sm text-gray-600 mb-3">
                          {dataset.abstract || dataset.description || 'No description available'}
                        </div>
                        {dataset.extent && (
                          <div className="text-xs text-gray-500 space-y-1 mb-3">
                            {dataset.extent.spatial && (
                              <div><strong>Spatial:</strong> {dataset.extent.spatial}</div>
                            )}
                            {dataset.extent.temporal && (
                              <div><strong>Temporal:</strong> {dataset.extent.temporal}</div>
                            )}
                          </div>
                        )}
                        <div className="flex gap-2">
                          <Button 
                            onClick={() => analyzeDataset(dataset)} 
                            disabled={loading}
                            className="flex-1"
                            size="sm"
                          >
                            <FileText className="h-4 w-4 mr-2" />
                            Analyze with AI
                          </Button>
                          <Button 
                            variant="outline"
                            size="sm"
                            asChild
                          >
                            <a 
                              href={dataset.url || `https://obis.org/dataset/${dataset.id}`} 
                              target="_blank" 
                              rel="noopener noreferrer"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {totalPages > 1 && (
                <div className="flex justify-center gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                    disabled={currentPage === 0 || loading}
                  >
                    Previous
                  </Button>
                  <span className="flex items-center px-4">
                    Page {currentPage + 1} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
                    disabled={currentPage >= totalPages - 1 || loading}
                  >
                    Next
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Dataset Analysis Results
              </CardTitle>
              <CardDescription>
                AI-powered analysis of selected OBIS dataset
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedDataset ? (
                <div className="space-y-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-medium text-blue-900">{selectedDataset.title}</h3>
                    <p className="text-sm text-blue-700 mt-1">Dataset ID: {selectedDataset.id}</p>
                    {selectedDataset.records && (
                      <p className="text-sm text-blue-700">Records: {selectedDataset.records.toLocaleString()}</p>
                    )}
                  </div>

                  {datasetAnalysis && (
                    <Card className="bg-gray-50">
                      <CardContent className="pt-6">
                        {datasetAnalysis.error ? (
                          <div className="text-red-600">
                            <strong>Error:</strong> {datasetAnalysis.error}
                          </div>
                        ) : (
                          <div className="space-y-4">
                            <Badge variant="secondary">AI Analysis Complete</Badge>
                            
                            <div>
                              <h4 className="font-medium mb-2">Dataset Overview:</h4>
                              <p className="text-sm text-gray-600">
                                {selectedDataset.records ? `${selectedDataset.records.toLocaleString()} records` : 'Unknown record count'} 
                                from OBIS dataset "{selectedDataset.title}"
                              </p>
                            </div>
                            
                            <div>
                              <h4 className="font-medium mb-2">AI Analysis:</h4>
                              <Markdown content={datasetAnalysis.ai_analysis} className="text-sm" />
                            </div>
                            
                            {datasetAnalysis.summary && (
                              <div>
                                <h4 className="font-medium mb-2">Summary:</h4>
                                <Markdown content={datasetAnalysis.summary} className="text-sm" />
                              </div>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Select a dataset from the Browse tab to see AI analysis results here.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="statistics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                OBIS Global Statistics
              </CardTitle>
              <CardDescription>
                Real-time statistics from the OBIS marine biodiversity database
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin mr-2" />
                  <span>Loading statistics...</span>
                </div>
              ) : statistics ? (
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
                  <p>Statistics not available at the moment.</p>
                  <Button onClick={loadStatistics} variant="outline" className="mt-4">
                    <Activity className="h-4 w-4 mr-2" />
                    Retry Loading
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Datasets;