// ============================================================================
// VoiceSelector Component - Voice Selection and Management Interface
// ============================================================================
//
// @file VoiceSelector.tsx
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description React component for voice selection and management
//
// This component provides a complete voice management interface with:
// - Voice listing with search and filtering capabilities
// - Voice preview functionality
// - Gender, style, and language filtering
// - Premium voice indicators
// - Voice selection and management
// - Loading states and error handling
// - Responsive design and accessibility
// ============================================================================

import React, { useState, useCallback, useMemo } from 'react';
import styled from 'styled-components';
import { useVoices, useSynthesizeText } from '../../../services/AudioService';
import { Voice, VoiceGender, VoiceStyle } from '../../../proto/audio';
import AudioPlayer from '../AudioPlayer/AudioPlayer';

// ============================================================================
// Types
// ============================================================================

export interface VoiceSelectorProps {
  selectedVoiceId?: string;
  onVoiceSelect?: (voice: Voice) => void;
  showPreview?: boolean;
  showFilters?: boolean;
  maxVoices?: number;
  className?: string;
}

interface FilterState {
  searchQuery: string;
  gender?: VoiceGender;
  style?: VoiceStyle;
  language?: string;
  premiumOnly: boolean;
}

// ============================================================================
// Styled Components
// ============================================================================

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  max-width: 600px;
`;

const Header = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  gap: 16px;
`;

const Title = styled.h3`
  margin: 0;
  color: ${props => props.theme?.colors?.text || '#212529'};
  font-size: 18px;
  font-weight: 600;
`;

const FiltersContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px;
  background: ${props => props.theme?.colors?.background || '#ffffff'};
  border-radius: 8px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
`;

const SearchInput = styled.input`
  flex: 1;
  min-width: 200px;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
  color: ${props => props.theme?.colors?.text || '#212529'};
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme?.colors?.primary || '#007bff'};
    box-shadow: 0 0 0 2px ${props => props.theme?.colors?.primary || '#007bff'}20;
  }
  
  &::placeholder {
    color: ${props => props.theme?.colors?.muted || '#6c757d'};
  }
`;

const FilterSelect = styled.select`
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
  background: ${props => props.theme?.colors?.surface || '#f8f9fa'};
  color: ${props => props.theme?.colors?.text || '#212529'};
  font-size: 14px;
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme?.colors?.primary || '#007bff'};
  }
`;

const FilterCheckbox = styled.label`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: ${props => props.theme?.colors?.text || '#212529'};
  cursor: pointer;
  
  input[type="checkbox"] {
    margin: 0;
  }
`;

const VoiceList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
`;

const VoiceCard = styled.div<{ isSelected: boolean }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: ${props => props.isSelected 
    ? props.theme?.colors?.primary || '#007bff'
    : props.theme?.colors?.background || '#ffffff'
  };
  color: ${props => props.isSelected 
    ? '#ffffff'
    : props.theme?.colors?.text || '#212529'
  };
  border: 1px solid ${props => props.isSelected 
    ? props.theme?.colors?.primary || '#007bff'
    : props.theme?.colors?.border || '#dee2e6'
  };
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
`;

const VoiceInfo = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const VoiceName = styled.div`
  font-weight: 600;
  font-size: 16px;
`;

const VoiceDetails = styled.div`
  font-size: 14px;
  opacity: 0.8;
`;

const VoiceDescription = styled.div`
  font-size: 12px;
  opacity: 0.7;
  margin-top: 2px;
`;

const VoiceActions = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const PreviewButton = styled.button<{ isSelected?: boolean }>`
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid ${props => props.isSelected 
    ? 'rgba(255, 255, 255, 0.3)'
    : props.theme?.colors?.border || '#dee2e6'
  };
  background: ${props => props.isSelected 
    ? 'rgba(255, 255, 255, 0.1)'
    : props.theme?.colors?.surface || '#f8f9fa'
  };
  color: ${props => props.isSelected 
    ? '#ffffff'
    : props.theme?.colors?.text || '#212529'
  };
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.isSelected 
      ? 'rgba(255, 255, 255, 0.2)'
      : props.theme?.colors?.hover || '#e9ecef'
    };
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const PremiumBadge = styled.span`
  padding: 2px 6px;
  border-radius: 3px;
  background: ${props => props.theme?.colors?.warning || '#ffc107'};
  color: ${props => props.theme?.colors?.dark || '#212529'};
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  
  &::after {
    content: '';
    width: 32px;
    height: 32px;
    border: 3px solid ${props => props.theme?.colors?.muted || '#adb5bd'};
    border-top: 3px solid ${props => props.theme?.colors?.primary || '#007bff'};
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  padding: 16px;
  border-radius: 6px;
  background: ${props => props.theme?.colors?.danger || '#dc3545'}10;
  color: ${props => props.theme?.colors?.danger || '#dc3545'};
  text-align: center;
  font-size: 14px;
`;

const EmptyState = styled.div`
  padding: 40px;
  text-align: center;
  color: ${props => props.theme?.colors?.muted || '#6c757d'};
  font-size: 14px;
`;

const PreviewContainer = styled.div`
  margin-top: 12px;
  padding: 12px;
  background: ${props => props.theme?.colors?.background || '#ffffff'};
  border-radius: 6px;
  border: 1px solid ${props => props.theme?.colors?.border || '#dee2e6'};
`;

// ============================================================================
// VoiceSelector Component
// ============================================================================

export const VoiceSelector: React.FC<VoiceSelectorProps> = ({
  selectedVoiceId,
  onVoiceSelect,
  showPreview = true,
  showFilters = true,
  maxVoices = 50,
  className,
}) => {
  // State
  const [filters, setFilters] = useState<FilterState>({
    searchQuery: '',
    premiumOnly: false,
  });
  const [previewVoiceId, setPreviewVoiceId] = useState<string | null>(null);
  const [previewAudio, setPreviewAudio] = useState<Uint8Array | null>(null);

  // Hooks
  const { data: voices, isLoading, error } = useVoices(filters);
  const synthesizeText = useSynthesizeText();

  // ============================================================================
  // Filter Handlers
  // ============================================================================

  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, searchQuery: event.target.value }));
  }, []);

  const handleGenderChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    setFilters(prev => ({ 
      ...prev, 
      gender: value ? parseInt(value) as VoiceGender : undefined 
    }));
  }, []);

  const handleStyleChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    setFilters(prev => ({ 
      ...prev, 
      style: value ? parseInt(value) as VoiceStyle : undefined 
    }));
  }, []);

  const handleLanguageChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>) => {
    setFilters(prev => ({ ...prev, language: event.target.value || undefined }));
  }, []);

  const handlePremiumToggle = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, premiumOnly: event.target.checked }));
  }, []);

  // ============================================================================
  // Voice Handlers
  // ============================================================================

  const handleVoiceSelect = useCallback((voice: Voice) => {
    onVoiceSelect?.(voice);
  }, [onVoiceSelect]);

  const handlePreview = useCallback(async (voice: Voice) => {
    if (!voice.metadata?.resourceId) return;

    try {
      setPreviewVoiceId(voice.metadata.resourceId);
      setPreviewAudio(null);

      const previewText = voice.previewText || `Hello! I'm ${voice.name}. This is how I sound.`;
      
      const audioData = await synthesizeText.mutateAsync({
        text: previewText,
        voiceId: voice.metadata.resourceId,
      });

      setPreviewAudio(audioData);
    } catch (error) {
      console.error('Preview failed:', error);
      setPreviewVoiceId(null);
    }
  }, [synthesizeText]);

  // ============================================================================
  // Computed Values
  // ============================================================================

  const filteredVoices = useMemo(() => {
    if (!voices) return [];
    
    let filtered = voices;

    // Apply search filter
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase();
      filtered = filtered.filter(voice =>
        voice.name?.toLowerCase().includes(query) ||
        voice.displayName?.toLowerCase().includes(query) ||
        voice.description?.toLowerCase().includes(query)
      );
    }

    // Apply max voices limit
    return filtered.slice(0, maxVoices);
  }, [voices, filters.searchQuery, maxVoices]);

  const uniqueLanguages = useMemo(() => {
    if (!voices) return [];
    const languages = voices.map(voice => voice.language).filter(Boolean);
    return Array.from(new Set(languages));
  }, [voices]);

  // ============================================================================
  // Render Helpers
  // ============================================================================

  const renderFilters = () => {
    if (!showFilters) return null;

    return (
      <FiltersContainer>
        <SearchInput
          type="text"
          placeholder="Search voices..."
          value={filters.searchQuery}
          onChange={handleSearchChange}
        />

        <FilterSelect value={filters.gender || ''} onChange={handleGenderChange}>
          <option value="">All Genders</option>
          <option value={VoiceGender.VOICE_GENDER_MALE}>Male</option>
          <option value={VoiceGender.VOICE_GENDER_FEMALE}>Female</option>
          <option value={VoiceGender.VOICE_GENDER_NEUTRAL}>Neutral</option>
          <option value={VoiceGender.VOICE_GENDER_CHILD}>Child</option>
        </FilterSelect>

        <FilterSelect value={filters.style || ''} onChange={handleStyleChange}>
          <option value="">All Styles</option>
          <option value={VoiceStyle.VOICE_STYLE_CONVERSATIONAL}>Conversational</option>
          <option value={VoiceStyle.VOICE_STYLE_PROFESSIONAL}>Professional</option>
          <option value={VoiceStyle.VOICE_STYLE_FRIENDLY}>Friendly</option>
          <option value={VoiceStyle.VOICE_STYLE_AUTHORITATIVE}>Authoritative</option>
          <option value={VoiceStyle.VOICE_STYLE_CALM}>Calm</option>
          <option value={VoiceStyle.VOICE_STYLE_ENERGETIC}>Energetic</option>
          <option value={VoiceStyle.VOICE_STYLE_DRAMATIC}>Dramatic</option>
        </FilterSelect>

        <FilterSelect value={filters.language || ''} onChange={handleLanguageChange}>
          <option value="">All Languages</option>
          {uniqueLanguages.map(language => (
            <option key={language} value={language}>{language}</option>
          ))}
        </FilterSelect>

        <FilterCheckbox>
          <input
            type="checkbox"
            checked={filters.premiumOnly}
            onChange={handlePremiumToggle}
          />
          Premium only
        </FilterCheckbox>
      </FiltersContainer>
    );
  };

  const renderVoiceCard = (voice: Voice) => {
    const isSelected = voice.metadata?.resourceId === selectedVoiceId;
    const isPreviewLoading = previewVoiceId === voice.metadata?.resourceId && synthesizeText.isPending;

    return (
      <VoiceCard
        key={voice.metadata?.resourceId}
        isSelected={isSelected}
        onClick={() => handleVoiceSelect(voice)}
      >
        <VoiceInfo>
          <VoiceName>
            {voice.displayName || voice.name}
            {voice.isPremium && <PremiumBadge>Premium</PremiumBadge>}
          </VoiceName>
          <VoiceDetails>
            {voice.language} • {VoiceGender[voice.gender || 0]} • {VoiceStyle[voice.style || 0]}
          </VoiceDetails>
          {voice.description && (
            <VoiceDescription>{voice.description}</VoiceDescription>
          )}
        </VoiceInfo>

        {showPreview && (
          <VoiceActions>
            <PreviewButton
              isSelected={isSelected}
              onClick={(e) => {
                e.stopPropagation();
                handlePreview(voice);
              }}
              disabled={isPreviewLoading}
            >
              {isPreviewLoading ? 'Loading...' : 'Preview'}
            </PreviewButton>
          </VoiceActions>
        )}
      </VoiceCard>
    );
  };

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <Container className={className}>
      <Header>
        <Title>Select Voice</Title>
      </Header>

      {renderFilters()}

      {isLoading && <LoadingSpinner />}

      {error && (
        <ErrorMessage>
          Failed to load voices: {error.message}
        </ErrorMessage>
      )}

      {!isLoading && !error && filteredVoices.length === 0 && (
        <EmptyState>
          No voices found matching your criteria.
        </EmptyState>
      )}

      {!isLoading && !error && filteredVoices.length > 0 && (
        <VoiceList>
          {filteredVoices.map(renderVoiceCard)}
        </VoiceList>
      )}

      {previewAudio && (
        <PreviewContainer>
          <AudioPlayer
            audioData={previewAudio}
            autoPlay={true}
            showControls={true}
            showWaveform={true}
          />
        </PreviewContainer>
      )}
    </Container>
  );
};

export default VoiceSelector;
