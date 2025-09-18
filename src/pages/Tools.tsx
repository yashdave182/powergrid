import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Search, Upload, Microscope, TreePine, Dna, Eye, FileImage } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Tools = () => {
  const [selectedTaxonomy, setSelectedTaxonomy] = useState("");
  const [uploadedOtolith, setUploadedOtolith] = useState<string | null>(null);
  const [ednaSequence, setEdnaSequence] = useState("");
  const { toast } = useToast();

  const taxonomyHierarchy = [
    {
      kingdom: "Animalia",
      phylum: "Chordata",
      class: "Actinopterygii",
      families: [
        {
          name: "Scombridae",
          species: ["Thunnus albacares (Yellowfin Tuna)", "Katsuwonus pelamis (Skipjack Tuna)"]
        },
        {
          name: "Clupeidae", 
          species: ["Sardinella longiceps (Oil Sardine)", "Stolephorus commersonnii (Commerson's Anchovy)"]
        },
        {
          name: "Carangidae",
          species: ["Decapterus russelli (Indian Scad)", "Selar crumenophthalmus (Bigeye Scad)"]
        }
      ]
    }
  ];

  const speciesMatches = [
    { species: "Sardinella longiceps", commonName: "Oil Sardine", confidence: 95.2, region: "Indian Ocean" },
    { species: "Sardinella gibbosa", commonName: "Goldstripe Sardine", confidence: 89.1, region: "Indo-Pacific" },
    { species: "Sardinella fimbriata", commonName: "Fringescale Sardine", confidence: 76.3, region: "Arabian Sea" },
  ];

  const handleOtolithUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedOtolith(e.target?.result as string);
        toast({
          title: "Otolith image uploaded",
          description: "Image processed and ready for analysis",
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const analyzeSequence = () => {
    if (ednaSequence.trim()) {
      toast({
        title: "eDNA analysis complete",
        description: "Sequence matched against marine species database",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-depth p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Specialized Tools</h1>
          <p className="text-muted-foreground">Advanced tools for marine species identification and analysis</p>
        </div>

        <Tabs defaultValue="taxonomy" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="taxonomy">Taxonomy</TabsTrigger>
            <TabsTrigger value="otolith">Otolith Viewer</TabsTrigger>
            <TabsTrigger value="edna">eDNA Analysis</TabsTrigger>
          </TabsList>

          <TabsContent value="taxonomy" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TreePine className="h-5 w-5" />
                  <span>Taxonomy Explorer</span>
                </CardTitle>
                <CardDescription>
                  Search and explore the hierarchical classification of marine species
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Search */}
                <div className="flex space-x-2">
                  <div className="flex-1">
                    <Label htmlFor="species-search">Search Species</Label>
                    <Input 
                      id="species-search"
                      placeholder="Enter species name, family, or common name..."
                      className="mt-1"
                    />
                  </div>
                  <Button className="mt-6 bg-gradient-ocean">
                    <Search className="h-4 w-4 mr-2" />
                    Search
                  </Button>
                </div>

                {/* Taxonomy Tree */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Marine Fish Classification</h3>
                  {taxonomyHierarchy.map((kingdom, idx) => (
                    <div key={idx} className="border border-border rounded-lg p-4">
                      <div className="space-y-3">
                        <div className="text-sm">
                          <span className="font-medium">Kingdom:</span> {kingdom.kingdom} → 
                          <span className="font-medium"> Phylum:</span> {kingdom.phylum} → 
                          <span className="font-medium"> Class:</span> {kingdom.class}
                        </div>
                        
                        <div className="space-y-3">
                          {kingdom.families.map((family, familyIdx) => (
                            <div key={familyIdx} className="ml-4 p-3 bg-muted/50 rounded-lg">
                              <div className="flex items-center space-x-2 mb-2">
                                <Badge variant="outline">Family</Badge>
                                <span className="font-medium">{family.name}</span>
                              </div>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 ml-4">
                                {family.species.map((species, speciesIdx) => (
                                  <div key={speciesIdx} className="flex items-center space-x-2 p-2 bg-background rounded border border-border/50">
                                    <Badge variant="secondary" className="text-xs">Species</Badge>
                                    <span className="text-sm italic">{species}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button variant="outline" className="justify-start">
                    <Search className="h-4 w-4 mr-2" />
                    Browse by Region
                  </Button>
                  <Button variant="outline" className="justify-start">
                    <TreePine className="h-4 w-4 mr-2" />
                    View Full Tree
                  </Button>
                  <Button variant="outline" className="justify-start">
                    <FileImage className="h-4 w-4 mr-2" />
                    Export Classification
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="otolith" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Microscope className="h-5 w-5" />
                  <span>Otolith Viewer & Analyzer</span>
                </CardTitle>
                <CardDescription>
                  Upload and analyze otolith images for species identification and age determination
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Upload Section */}
                <div className="border-2 border-dashed border-border rounded-lg p-8">
                  {uploadedOtolith ? (
                    <div className="space-y-4">
                      <div className="relative">
                        <img 
                          src={uploadedOtolith} 
                          alt="Uploaded otolith" 
                          className="max-w-full h-64 object-contain mx-auto rounded-lg shadow-lg"
                        />
                        <div className="absolute inset-0 border-2 border-primary/50 rounded-lg pointer-events-none"></div>
                      </div>
                      <div className="text-center space-y-2">
                        <h3 className="font-semibold">Otolith Analysis Results</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div className="p-3 bg-muted rounded-lg">
                            <div className="font-medium">Estimated Age</div>
                            <div className="text-xl font-bold text-primary">3.2 years</div>
                          </div>
                          <div className="p-3 bg-muted rounded-lg">
                            <div className="font-medium">Length (mm)</div>
                            <div className="text-xl font-bold text-accent">12.4 × 8.7</div>
                          </div>
                          <div className="p-3 bg-muted rounded-lg">
                            <div className="font-medium">Shape Index</div>
                            <div className="text-xl font-bold text-green-600">1.43</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center space-y-4">
                      <Upload className="h-16 w-16 text-muted-foreground mx-auto" />
                      <div>
                        <h3 className="text-lg font-semibold mb-2">Upload Otolith Image</h3>
                        <p className="text-muted-foreground mb-4">
                          Supported formats: JPG, PNG (Max 10MB)
                        </p>
                      </div>
                    </div>
                  )}
                  
                  <div className="text-center">
                    <Input
                      type="file"
                      accept="image/*"
                      onChange={handleOtolithUpload}
                      className="hidden"
                      id="otolith-upload"
                    />
                    <Button asChild className="bg-gradient-ocean">
                      <label htmlFor="otolith-upload" className="cursor-pointer">
                        <Upload className="h-4 w-4 mr-2" />
                        {uploadedOtolith ? "Upload New Image" : "Select Otolith Image"}
                      </label>
                    </Button>
                  </div>
                </div>

                {/* Analysis Tools */}
                {uploadedOtolith && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Morphometric Analysis</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <Button variant="outline" className="w-full justify-start">
                          <Eye className="h-4 w-4 mr-2" />
                          Measure Length/Width
                        </Button>
                        <Button variant="outline" className="w-full justify-start">
                          <Microscope className="h-4 w-4 mr-2" />
                          Count Growth Rings
                        </Button>
                        <Button variant="outline" className="w-full justify-start">
                          <TreePine className="h-4 w-4 mr-2" />
                          Shape Analysis
                        </Button>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Species Identification</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="text-sm">
                          <div className="font-medium mb-2">Likely Species:</div>
                          <div className="space-y-2">
                            <div className="flex justify-between items-center p-2 bg-muted rounded">
                              <span className="italic">Sardinella longiceps</span>
                              <Badge>89% match</Badge>
                            </div>
                            <div className="flex justify-between items-center p-2 bg-muted rounded">
                              <span className="italic">Rastrelliger kanagurta</span>
                              <Badge variant="outline">76% match</Badge>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="edna" className="space-y-6">
            <Card className="shadow-float">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Dna className="h-5 w-5" />
                  <span>Environmental DNA (eDNA) Analysis</span>
                </CardTitle>
                <CardDescription>
                  Analyze DNA sequences for species identification and biodiversity assessment
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Sequence Input */}
                <div className="space-y-4">
                  <Label htmlFor="dna-sequence">DNA Sequence (FASTA format)</Label>
                  <Textarea
                    id="dna-sequence"
                    value={ednaSequence}
                    onChange={(e) => setEdnaSequence(e.target.value)}
                    placeholder="Enter DNA sequence here... 
>Sample_Sequence_1
ATCGATCGATCGATCGTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC
GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT
AGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG..."
                    className="min-h-[150px] font-mono text-sm"
                  />
                  <div className="flex space-x-2">
                    <Button onClick={analyzeSequence} className="bg-gradient-coral">
                      <Dna className="h-4 w-4 mr-2" />
                      Analyze Sequence
                    </Button>
                    <Button variant="outline">
                      <Upload className="h-4 w-4 mr-2" />
                      Upload FASTA File
                    </Button>
                  </div>
                </div>

                {/* Results */}
                {ednaSequence && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Species Matches</h3>
                    <div className="space-y-3">
                      {speciesMatches.map((match, index) => (
                        <div key={index} className="p-4 border border-border rounded-lg hover:shadow-float transition-shadow">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h4 className="font-medium italic">{match.species}</h4>
                              <p className="text-sm text-muted-foreground">{match.commonName}</p>
                            </div>
                            <Badge 
                              variant={match.confidence > 90 ? "default" : "outline"}
                              className={match.confidence > 90 ? "bg-green-100 text-green-800" : ""}
                            >
                              {match.confidence}% match
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Region: {match.region}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Analysis Options */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Analysis Parameters</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label>Database</Label>
                        <select className="w-full mt-1 p-2 border border-border rounded-md">
                          <option>NCBI GenBank</option>
                          <option>BOLD Systems</option>
                          <option>Marine Species Database</option>
                        </select>
                      </div>
                      <div>
                        <Label>Similarity Threshold</Label>
                        <select className="w-full mt-1 p-2 border border-border rounded-md">
                          <option>95% (High confidence)</option>
                          <option>90% (Medium confidence)</option>
                          <option>85% (Low confidence)</option>
                        </select>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Tools;