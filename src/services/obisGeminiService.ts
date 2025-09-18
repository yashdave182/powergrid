// Enhanced OBIS + Gemini API Integration Service
import { geminiApi } from './geminiApi';

interface OBISSpeciesData {
  scientificName?: string;
  kingdom?: string;
  phylum?: string;
  class?: string;
  order?: string;
  family?: string;
  genus?: string;
  species?: string;
  decimalLatitude?: number;
  decimalLongitude?: number;
  depth?: number;
  minimumDepthInMeters?: number;
  maximumDepthInMeters?: number;
  eventDate?: string;
  locality?: string;
  country?: string;
  individualCount?: number;
  basisOfRecord?: string;
  datasetName?: string;
  institutionCode?: string;
}

interface OBISResponse {
  total: number;
  results: OBISSpeciesData[];
  limit: number;
  offset: number;
}

interface OBISDataset {
  id: string;
  title: string;
  description?: string;
  citation?: string;
  license?: string;
  records?: number;
  extent?: {
    spatial?: string;
    temporal?: string;
  };
}

interface EnhancedMarineAnalysis {
  obis_data: OBISResponse | OBISDataset;
  ai_analysis: string;
  insights: {
    species_diversity: string;
    geographic_distribution: string;
    conservation_status: string;
    ecological_significance: string;
    threats_and_recommendations: string;
  };
  summary: string;
}

class OBISGeminiService {
  private obisBaseUrl = 'https://api.obis.org/v3';

  async searchSpeciesWithAI(
    scientificName?: string,
    geometry?: string,
    limit: number = 100
  ): Promise<EnhancedMarineAnalysis> {
    try {
      // 1. Fetch data from OBIS API
      const obisData = await this.fetchOBISSpecies(scientificName, geometry, limit);
      
      // 2. Analyze with Gemini AI
      const aiAnalysis = await this.analyzeSpeciesDataWithAI(obisData, scientificName);
      
      // 3. Generate detailed insights
      const insights = await this.generateDetailedInsights(obisData, scientificName);
      
      // 4. Create summary
      const summary = await this.generateSummary(obisData, aiAnalysis, scientificName);
      
      return {
        obis_data: obisData,
        ai_analysis: aiAnalysis,
        insights,
        summary
      };
    } catch (error) {
      console.error('Error in species analysis:', error);
      throw new Error(`Species analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async analyzeDatasetWithAI(datasetId: string): Promise<EnhancedMarineAnalysis> {
    try {
      // 1. Fetch dataset info from OBIS
      const datasetData = await this.fetchOBISDataset(datasetId);
      
      // 2. Analyze dataset with AI
      const aiAnalysis = await this.analyzeDatasetWithAI(datasetData);
      
      // 3. Generate insights for dataset
      const insights = await this.generateDatasetInsights(datasetData);
      
      // 4. Create summary
      const summary = await this.generateDatasetSummary(datasetData, aiAnalysis);
      
      return {
        obis_data: datasetData,
        ai_analysis: aiAnalysis,
        insights,
        summary
      };
    } catch (error) {
      console.error('Error in dataset analysis:', error);
      throw new Error(`Dataset analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async getMarineInsightsForRegion(
    geometry: string,
    description?: string
  ): Promise<string> {
    try {
      // 1. Get species data for the region
      const regionData = await this.fetchOBISSpecies(undefined, geometry, 50);
      
      // 2. Get region-specific insights from AI
      const prompt = `Analyze this marine biodiversity data for a specific region:

Region: ${description || 'Specified coordinates'}
Geometry: ${geometry}
Species data: ${JSON.stringify(regionData, null, 2)}

Please provide comprehensive insights about:
1. Biodiversity patterns in this region
2. Key species and their ecological roles
3. Environmental conditions and habitat characteristics
4. Conservation priorities and threats
5. Research opportunities and data gaps
6. Comparison with global marine biodiversity patterns

Format your response as a detailed scientific analysis suitable for researchers and conservationists.`;

      return await geminiApi.generateContent(prompt);
    } catch (error) {
      console.error('Error getting regional insights:', error);
      throw new Error(`Regional analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async fetchOBISSpecies(
    scientificName?: string,
    geometry?: string,
    limit: number = 100
  ): Promise<OBISResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: '0'
    });

    if (scientificName) {
      params.append('scientificname', scientificName);
    }
    if (geometry) {
      params.append('geometry', geometry);
    }

    const response = await fetch(`${this.obisBaseUrl}/occurrence?${params}`);
    
    if (!response.ok) {
      throw new Error(`OBIS API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  private async fetchOBISDataset(datasetId: string): Promise<OBISDataset> {
    const response = await fetch(`${this.obisBaseUrl}/dataset/${datasetId}`);
    
    if (!response.ok) {
      throw new Error(`OBIS Dataset API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  private async analyzeSpeciesDataWithAI(
    data: OBISResponse,
    scientificName?: string
  ): Promise<string> {
    const prompt = `As a marine biology expert, analyze this OBIS species occurrence data:

Query: ${scientificName || 'General marine species search'}
Total records: ${data.total}
Retrieved records: ${data.results.length}

Sample data:
${JSON.stringify(data.results.slice(0, 5), null, 2)}

Please provide a comprehensive analysis covering:
1. Species diversity and abundance patterns
2. Geographic distribution analysis
3. Depth and habitat preferences
4. Temporal patterns (if available)
5. Data quality assessment
6. Ecological implications
7. Conservation considerations

Focus on scientifically accurate insights that would be valuable for marine researchers and conservationists.`;

    return await geminiApi.generateContent(prompt);
  }

  private async analyzeDatasetWithAI(dataset: OBISDataset): Promise<string> {
    const prompt = `Analyze this OBIS dataset as a marine biology expert:

Dataset: ${dataset.title}
ID: ${dataset.id}
Description: ${dataset.description || 'No description available'}
Records: ${dataset.records || 'Unknown'}
Spatial extent: ${dataset.extent?.spatial || 'Not specified'}
Temporal extent: ${dataset.extent?.temporal || 'Not specified'}

Please provide analysis on:
1. Scientific significance of this dataset
2. Geographic and temporal coverage
3. Species coverage and taxonomic scope
4. Research applications and value
5. Data quality and completeness assessment
6. Integration opportunities with other datasets
7. Conservation and management implications

Provide insights suitable for marine researchers and data managers.`;

    return await geminiApi.generateContent(prompt);
  }

  private async generateDetailedInsights(
    data: OBISResponse,
    scientificName?: string
  ): Promise<EnhancedMarineAnalysis['insights']> {
    const species_diversity = await geminiApi.generateContent(
      `Analyze species diversity patterns from this OBIS data: ${JSON.stringify(data.results.slice(0, 10), null, 2)}. Focus on taxonomic diversity, abundance patterns, and biodiversity metrics.`
    );

    const geographic_distribution = await geminiApi.generateContent(
      `Analyze geographic distribution patterns from this OBIS data: ${JSON.stringify(data.results.slice(0, 10), null, 2)}. Focus on spatial patterns, biogeographic regions, and habitat preferences.`
    );

    const conservation_status = await geminiApi.generateContent(
      `Assess conservation implications from this OBIS data: ${JSON.stringify(data.results.slice(0, 10), null, 2)}. Focus on conservation status, threats, and protection needs.`
    );

    const ecological_significance = await geminiApi.generateContent(
      `Explain ecological significance from this OBIS data: ${JSON.stringify(data.results.slice(0, 10), null, 2)}. Focus on ecosystem roles, food web interactions, and ecological importance.`
    );

    const threats_and_recommendations = await geminiApi.generateContent(
      `Identify threats and provide recommendations based on this OBIS data: ${JSON.stringify(data.results.slice(0, 10), null, 2)}. Focus on current threats, future risks, and actionable conservation recommendations.`
    );

    return {
      species_diversity,
      geographic_distribution,
      conservation_status,
      ecological_significance,
      threats_and_recommendations
    };
  }

  private async generateDatasetInsights(dataset: OBISDataset): Promise<EnhancedMarineAnalysis['insights']> {
    const basePrompt = `Dataset: ${dataset.title} (${dataset.records} records)`;
    
    return {
      species_diversity: await geminiApi.generateContent(`${basePrompt} - Analyze expected species diversity patterns and taxonomic coverage.`),
      geographic_distribution: await geminiApi.generateContent(`${basePrompt} - Analyze geographic coverage and spatial distribution patterns.`),
      conservation_status: await geminiApi.generateContent(`${basePrompt} - Assess conservation value and implications.`),
      ecological_significance: await geminiApi.generateContent(`${basePrompt} - Explain ecological significance and research value.`),
      threats_and_recommendations: await geminiApi.generateContent(`${basePrompt} - Identify potential threats and research recommendations.`)
    };
  }

  private async generateSummary(
    data: OBISResponse,
    analysis: string,
    scientificName?: string
  ): Promise<string> {
    const prompt = `Create a concise executive summary of this marine biodiversity analysis:

Query: ${scientificName || 'Marine species search'}
Records found: ${data.total}
Analysis: ${analysis.substring(0, 500)}...

Provide a 2-3 paragraph summary highlighting:
1. Key findings about species and biodiversity
2. Geographic and ecological patterns
3. Most important conservation insights
4. Main recommendations for action

Keep it accessible for both scientists and policy makers.`;

    return await geminiApi.generateContent(prompt);
  }

  private async generateDatasetSummary(
    dataset: OBISDataset,
    analysis: string
  ): Promise<string> {
    const prompt = `Create an executive summary for this OBIS dataset analysis:

Dataset: ${dataset.title}
Records: ${dataset.records}
Analysis: ${analysis.substring(0, 500)}...

Provide a 2-3 paragraph summary highlighting:
1. Dataset scope and scientific value
2. Key applications and research potential
3. Conservation and management relevance
4. Integration opportunities

Target audience: marine researchers and data managers.`;

    return await geminiApi.generateContent(prompt);
  }

  // Helper method for quick species lookup with AI insights
  async quickSpeciesLookup(scientificName: string): Promise<string> {
    try {
      const data = await this.fetchOBISSpecies(scientificName, undefined, 20);
      
      if (data.total === 0) {
        return await geminiApi.generateContent(`No OBIS records found for "${scientificName}". Please provide general information about this species, including habitat, distribution, conservation status, and ecological importance.`);
      }

      const prompt = `Quick analysis for ${scientificName}:
Found ${data.total} records in OBIS database.
Sample data: ${JSON.stringify(data.results.slice(0, 3), null, 2)}

Provide a brief (3-4 sentences) summary covering:
- Current distribution based on OBIS data
- Habitat preferences
- Conservation significance
- Key ecological role`;

      return await geminiApi.generateContent(prompt);
    } catch (error) {
      console.error('Error in quick species lookup:', error);
      throw new Error(`Species lookup failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

export const obisGeminiService = new OBISGeminiService();