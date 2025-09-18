import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Upload, Search, Filter, FileText, Image, Database, Calendar, MapPin, Tag } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Datasets = () => {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const { toast } = useToast();

  const datasets = [
    {
      id: 1,
      name: "Arabian Sea Temperature Survey 2024",
      type: "CSV",
      size: "2.3 MB",
      species: "Mixed Pelagic",
      location: "Arabian Sea",
      date: "2024-01-15",
      parameters: ["Temperature", "Salinity", "pH"],
      status: "validated",
      records: 1250
    },
    {
      id: 2,
      name: "Coastal Fish Diversity Kerala",
      type: "JSON",
      size: "5.7 MB",
      species: "Coastal Fish",
      location: "Kerala Coast",
      date: "2024-02-20",
      parameters: ["Species Count", "Biomass", "Length"],
      status: "processing",
      records: 890
    },
    {
      id: 3,
      name: "Otolith Images Collection",
      type: "Images",
      size: "125 MB",
      species: "Various",
      location: "Multiple",
      date: "2024-03-10",
      parameters: ["Images", "Morphometry"],
      status: "validated",
      records: 340
    },
    {
      id: 4,
      name: "Monsoon Impact Study",
      type: "CSV",
      size: "8.2 MB",
      species: "Plankton",
      location: "Bay of Bengal",
      date: "2024-02-05",
      parameters: ["Abundance", "Diversity", "Environmental"],
      status: "validated",
      records: 2100
    }
  ];

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      toast({
        title: "Files uploaded successfully",
        description: `${files.length} file(s) have been processed and added to the queue.`,
      });
      setUploadDialogOpen(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "validated": return "bg-emerald-100 text-emerald-800 border-emerald-200";
      case "processing": return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "error": return "bg-red-100 text-red-800 border-red-200";
      default: return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "CSV": return <FileText className="h-4 w-4" />;
      case "JSON": return <Database className="h-4 w-4" />;
      case "Images": return <Image className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  const filteredDatasets = datasets.filter(dataset =>
    dataset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dataset.species.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dataset.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-depth p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Dataset Management</h1>
          <p className="text-muted-foreground">Upload, organize, and manage your marine research datasets</p>
        </div>

        <Tabs defaultValue="browse" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 lg:w-[400px]">
            <TabsTrigger value="browse">Browse Datasets</TabsTrigger>
            <TabsTrigger value="upload">Upload Data</TabsTrigger>
          </TabsList>

          <TabsContent value="browse" className="space-y-6">
            {/* Search and Filter */}
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Search className="h-5 w-5" />
                  <span>Search & Filter</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col lg:flex-row gap-4">
                  <div className="flex-1">
                    <Label htmlFor="search">Search datasets</Label>
                    <Input
                      id="search"
                      placeholder="Search by name, species, or location..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div className="lg:w-48">
                    <Label>Data Type</Label>
                    <Select>
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="All types" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="csv">CSV Files</SelectItem>
                        <SelectItem value="json">JSON Files</SelectItem>
                        <SelectItem value="images">Images</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="lg:w-48">
                    <Label>Status</Label>
                    <Select>
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="All statuses" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Statuses</SelectItem>
                        <SelectItem value="validated">Validated</SelectItem>
                        <SelectItem value="processing">Processing</SelectItem>
                        <SelectItem value="error">Error</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Datasets Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredDatasets.map((dataset) => (
                <Card key={dataset.id} className="shadow-float hover:shadow-ocean transition-all duration-300">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-gradient-ocean rounded-lg">
                          {getTypeIcon(dataset.type)}
                        </div>
                        <div>
                          <CardTitle className="text-lg">{dataset.name}</CardTitle>
                          <CardDescription>{dataset.size} • {dataset.records} records</CardDescription>
                        </div>
                      </div>
                      <Badge className={getStatusColor(dataset.status)}>
                        {dataset.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex items-center space-x-2">
                        <Tag className="h-4 w-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Species:</span>
                        <span className="font-medium">{dataset.species}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Location:</span>
                        <span className="font-medium">{dataset.location}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Date:</span>
                        <span className="font-medium">{dataset.date}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Database className="h-4 w-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Type:</span>
                        <span className="font-medium">{dataset.type}</span>
                      </div>
                    </div>
                    
                    <div>
                      <Label className="text-sm text-muted-foreground">Parameters</Label>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {dataset.parameters.map((param, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {param}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="flex space-x-2 pt-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        View Details
                      </Button>
                      <Button size="sm" className="flex-1 bg-gradient-ocean">
                        Download
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="upload" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Upload className="h-5 w-5" />
                  <span>Upload New Dataset</span>
                </CardTitle>
                <CardDescription>
                  Upload CSV, JSON, or image files for marine research data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* File Upload */}
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                  <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Drop files here or click to browse</h3>
                  <p className="text-muted-foreground mb-4">
                    Supported formats: CSV, JSON, JPG, PNG (Max 100MB)
                  </p>
                  <Input
                    type="file"
                    multiple
                    accept=".csv,.json,.jpg,.jpeg,.png"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <Button asChild className="bg-gradient-ocean">
                    <label htmlFor="file-upload" className="cursor-pointer">
                      Select Files
                    </label>
                  </Button>
                </div>

                {/* Metadata Form */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="dataset-name">Dataset Name</Label>
                      <Input id="dataset-name" placeholder="Enter dataset name" />
                    </div>
                    <div>
                      <Label htmlFor="species">Species</Label>
                      <Input id="species" placeholder="e.g., Coastal Fish, Plankton" />
                    </div>
                    <div>
                      <Label htmlFor="location">Sampling Location</Label>
                      <Input id="location" placeholder="e.g., Arabian Sea, Kerala Coast" />
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="date">Collection Date</Label>
                      <Input id="date" type="date" />
                    </div>
                    <div>
                      <Label htmlFor="parameters">Parameters Measured</Label>
                      <Input id="parameters" placeholder="e.g., Temperature, Salinity, pH" />
                    </div>
                    <div>
                      <Label htmlFor="description">Description</Label>
                      <Input id="description" placeholder="Brief description of the dataset" />
                    </div>
                  </div>
                </div>

                <div className="flex justify-end space-x-3">
                  <Button variant="outline">Save as Draft</Button>
                  <Button className="bg-gradient-ocean">Upload & Process</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Datasets;