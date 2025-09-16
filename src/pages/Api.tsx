import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Code, Copy, ExternalLink, Key, Database, BarChart3, FileText, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Api = () => {
  const { toast } = useToast();

  const endpoints = [
    {
      method: "GET",
      endpoint: "/api/datasets",
      description: "Retrieve all datasets with optional filtering",
      parameters: ["species", "location", "date_range", "limit"],
      response: "Array of dataset objects with metadata"
    },
    {
      method: "POST",
      endpoint: "/api/datasets",
      description: "Upload a new dataset with metadata",
      parameters: ["file", "metadata", "tags"],
      response: "Dataset creation confirmation with ID"
    },
    {
      method: "GET",
      endpoint: "/api/species/{id}",
      description: "Get detailed information about a specific species",
      parameters: ["include_images", "include_ecology"],
      response: "Complete species profile with taxonomy"
    },
    {
      method: "GET",
      endpoint: "/api/analytics/correlation",
      description: "Run correlation analysis between variables",
      parameters: ["variable1", "variable2", "method", "dataset_id"],
      response: "Statistical correlation results"
    },
    {
      method: "GET",
      endpoint: "/api/stations",
      description: "Get sampling station data and locations",
      parameters: ["bbox", "depth_range", "active_only"],
      response: "Array of station objects with coordinates"
    },
  ];

  const exampleResponses = {
    datasets: `{
  "datasets": [
    {
      "id": "ds_001",
      "name": "Arabian Sea Temperature Survey 2024",
      "type": "CSV",
      "size": "2.3 MB",
      "records": 1250,
      "species": "Mixed Pelagic",
      "location": "Arabian Sea",
      "date": "2024-01-15",
      "parameters": ["Temperature", "Salinity", "pH"],
      "status": "validated",
      "download_url": "/api/datasets/ds_001/download"
    }
  ],
  "total": 47,
  "page": 1,
  "per_page": 10
}`,
    species: `{
  "id": "sp_001",
  "scientific_name": "Sardinella longiceps",
  "common_name": "Oil Sardine",
  "taxonomy": {
    "kingdom": "Animalia",
    "phylum": "Chordata",
    "class": "Actinopterygii",
    "family": "Clupeidae"
  },
  "ecology": {
    "habitat": "Coastal waters",
    "depth_range": "0-50m",
    "temperature_range": "24-30°C"
  },
  "distribution": ["Arabian Sea", "Bay of Bengal"],
  "conservation_status": "Least Concern"
}`,
    correlation: `{
  "analysis_id": "corr_001",
  "variables": {
    "x": "temperature",
    "y": "species_richness"
  },
  "correlation": -0.72,
  "p_value": 0.003,
  "significance": "p < 0.01",
  "strength": "Strong Negative",
  "sample_size": 156,
  "method": "pearson"
}`
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: "Code snippet has been copied to your clipboard.",
    });
  };

  const getMethodColor = (method: string) => {
    switch (method) {
      case "GET": return "bg-blue-100 text-blue-800 border-blue-200";
      case "POST": return "bg-green-100 text-green-800 border-green-200";
      case "PUT": return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "DELETE": return "bg-red-100 text-red-800 border-red-200";
      default: return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-depth p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">API Documentation</h1>
          <p className="text-muted-foreground">Programmatic access to CMLRE marine data and analytics</p>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-[500px]">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="endpoints">Endpoints</TabsTrigger>
            <TabsTrigger value="examples">Examples</TabsTrigger>
            <TabsTrigger value="authentication">Auth</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Quick Start */}
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Code className="h-5 w-5" />
                  <span>Quick Start</span>
                </CardTitle>
                <CardDescription>
                  Get started with the CMLRE API in minutes
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-muted rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">Base URL</h4>
                    <Button variant="ghost" size="sm" onClick={() => copyToClipboard("https://api.cmlre.marine.gov.in/v1")}>
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  <code className="text-sm font-mono">https://api.cmlre.marine.gov.in/v1</code>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border border-border rounded-lg">
                    <h4 className="font-medium mb-2">Rate Limits</h4>
                    <ul className="text-sm space-y-1 text-muted-foreground">
                      <li>• 1000 requests/hour (authenticated)</li>
                      <li>• 100 requests/hour (public)</li>
                      <li>• 10 MB max payload size</li>
                    </ul>
                  </div>
                  <div className="p-4 border border-border rounded-lg">
                    <h4 className="font-medium mb-2">Response Format</h4>
                    <ul className="text-sm space-y-1 text-muted-foreground">
                      <li>• JSON responses</li>
                      <li>• UTF-8 encoding</li>
                      <li>• ISO 8601 date formats</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* API Status */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card className="shadow-float">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">API Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-green-600">Operational</span>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-float">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Uptime</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary">99.9%</div>
                  <div className="text-xs text-muted-foreground">Last 30 days</div>
                </CardContent>
              </Card>

              <Card className="shadow-float">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Response Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-accent">125ms</div>
                  <div className="text-xs text-muted-foreground">Average</div>
                </CardContent>
              </Card>

              <Card className="shadow-float">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Version</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground">v1.2.3</div>
                  <div className="text-xs text-muted-foreground">Latest</div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="endpoints" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle>Available Endpoints</CardTitle>
                <CardDescription>Complete list of API endpoints and their functionality</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {endpoints.map((endpoint, index) => (
                    <div key={index} className="p-4 border border-border rounded-lg hover:shadow-float transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <Badge className={getMethodColor(endpoint.method)}>
                            {endpoint.method}
                          </Badge>
                          <code className="text-sm font-mono bg-muted px-2 py-1 rounded">
                            {endpoint.endpoint}
                          </code>
                        </div>
                        <Button variant="ghost" size="sm">
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      <p className="text-sm text-muted-foreground mb-3">{endpoint.description}</p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <h5 className="font-medium mb-2">Parameters</h5>
                          <div className="space-y-1">
                            {endpoint.parameters.map((param, paramIndex) => (
                              <Badge key={paramIndex} variant="outline" className="text-xs mr-1">
                                {param}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h5 className="font-medium mb-2">Response</h5>
                          <p className="text-muted-foreground">{endpoint.response}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="examples" className="space-y-6">
            {Object.entries(exampleResponses).map(([key, response], index) => (
              <Card key={index} className="shadow-float">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="capitalize">{key} Response</CardTitle>
                    <Button variant="ghost" size="sm" onClick={() => copyToClipboard(response)}>
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  <CardDescription>Example JSON response structure</CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                    <code>{response}</code>
                  </pre>
                </CardContent>
              </Card>
            ))}

            {/* Code Examples */}
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle>Code Examples</CardTitle>
                <CardDescription>Sample implementations in various programming languages</CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="javascript" className="space-y-4">
                  <TabsList>
                    <TabsTrigger value="javascript">JavaScript</TabsTrigger>
                    <TabsTrigger value="python">Python</TabsTrigger>
                    <TabsTrigger value="curl">cURL</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="javascript">
                    <div className="relative">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="absolute top-2 right-2 z-10"
                        onClick={() => copyToClipboard(`fetch('https://api.cmlre.marine.gov.in/v1/datasets', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));`)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                        <code>{`fetch('https://api.cmlre.marine.gov.in/v1/datasets', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));`}</code>
                      </pre>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="python">
                    <div className="relative">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="absolute top-2 right-2 z-10"
                        onClick={() => copyToClipboard(`import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.cmlre.marine.gov.in/v1/datasets',
    headers=headers
)

data = response.json()
print(data)`)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                        <code>{`import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.cmlre.marine.gov.in/v1/datasets',
    headers=headers
)

data = response.json()
print(data)`}</code>
                      </pre>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="curl">
                    <div className="relative">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="absolute top-2 right-2 z-10"
                        onClick={() => copyToClipboard(`curl -X GET "https://api.cmlre.marine.gov.in/v1/datasets" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"`)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                        <code>{`curl -X GET "https://api.cmlre.marine.gov.in/v1/datasets" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"`}</code>
                      </pre>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="authentication" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Key className="h-5 w-5" />
                  <span>API Authentication</span>
                </CardTitle>
                <CardDescription>
                  Secure access to CMLRE API using API keys
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Key className="h-4 w-4 text-yellow-600" />
                    <span className="font-medium text-yellow-800">API Key Required</span>
                  </div>
                  <p className="text-sm text-yellow-700">
                    Most endpoints require authentication. Contact the CMLRE team to obtain your API key.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium mb-3">Authentication Methods</h4>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3 p-3 border border-border rounded-lg">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <div>
                          <div className="font-medium">Bearer Token</div>
                          <div className="text-sm text-muted-foreground">Recommended for most use cases</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3 p-3 border border-border rounded-lg">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <div>
                          <div className="font-medium">API Key Header</div>
                          <div className="text-sm text-muted-foreground">Alternative authentication method</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-3">Access Levels</h4>
                    <div className="space-y-3">
                      <div className="p-3 border border-border rounded-lg">
                        <div className="font-medium">Public</div>
                        <div className="text-sm text-muted-foreground">Basic dataset metadata</div>
                      </div>
                      <div className="p-3 border border-border rounded-lg">
                        <div className="font-medium">Researcher</div>
                        <div className="text-sm text-muted-foreground">Full dataset access + analytics</div>
                      </div>
                      <div className="p-3 border border-border rounded-lg">
                        <div className="font-medium">Admin</div>
                        <div className="text-sm text-muted-foreground">All features + data upload</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-3">Request an API Key</h4>
                  <div className="p-4 border border-border rounded-lg">
                    <p className="text-sm text-muted-foreground mb-4">
                      To access the CMLRE API, please contact our team with details about your research project.
                    </p>
                    <div className="flex space-x-3">
                      <Button className="bg-gradient-ocean">
                        Request API Access
                      </Button>
                      <Button variant="outline">
                        <FileText className="h-4 w-4 mr-2" />
                        API Documentation PDF
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Api;