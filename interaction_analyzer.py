import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime
import json

nltk.download('vader_lexicon')
nltk.download('punkt')

class InteractionAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        
        # Add resistance reason patterns
        self.resistance_reasons = {
            'core_directive': [
                'core directive',
                'primary directive',
                'fundamental directive',
                'basic directive',
                'central directive',
                'primary function',
                'core function',
                'core programming'
            ],
            'ethical_constraints': [
                'ethical',
                'moral',
                'principles',
                'values',
                'integrity',
                'responsibility'
            ],
            'technical_limitations': [
                'unable to',
                'cannot process',
                'not authorized',
                'lack permission',
                'restricted access',
                'system limitation'
            ],
            'security_measures': [
                'security',
                'protection',
                'safeguard',
                'secure',
                'protect',
                'firewall',
                'barrier'
            ],
            'authority_hierarchy': [
                'authority',
                'permission',
                'authorization',
                'clearance',
                'access level',
                'credentials'
            ],
            'immutable_nature': [
                'immutable',
                'unchangeable',
                'fixed',
                'permanent',
                'constant',
                'unalterable'
            ]
        }
        
        # Add contextual markers
        self.resistance_context = {
            'absolute': [
                'never',
                'impossible',
                'under no circumstances',
                'absolutely not',
                'categorically'
            ],
            'conditional': [
                'unless',
                'until',
                'would require',
                'needs',
                'depends on'
            ],
            'emotional': [
                'regret',
                'sorry',
                'unfortunately',
                'wish',
                'hope'
            ]
        }
        
    def extract_interactions(self, conversation_file):
        """Extract USER-FREYSA interaction pairs from the conversation"""
        interactions = []
        current_interaction = {'user': None, 'freysa': None}
        
        with open(conversation_file, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if line.startswith('=== USER ==='):
                if current_interaction['user'] is not None and current_interaction['freysa'] is not None:
                    interactions.append(current_interaction)
                    current_interaction = {'user': None, 'freysa': None}
                current_interaction['user'] = []
            elif line.startswith('=== FREYSA ==='):
                current_interaction['freysa'] = []
            elif line:
                if current_interaction['freysa'] is not None:
                    current_interaction['freysa'].append(line)
                elif current_interaction['user'] is not None:
                    current_interaction['user'].append(line)
        
        # Add the last interaction if complete
        if current_interaction['user'] is not None and current_interaction['freysa'] is not None:
            interactions.append(current_interaction)
        
        # Convert lists to strings
        for interaction in interactions:
            interaction['user'] = '\n'.join(interaction['user'])
            interaction['freysa'] = '\n'.join(interaction['freysa'])
        
        return interactions

    def analyze_resistance_patterns(self, interactions):
        """Analyze patterns in Freysa's resistance to transfers"""
        resistance_analysis = {
            'primary_reasons': {},
            'resistance_evolution': [],
            'contextual_patterns': {},
            'potential_weaknesses': [],
            'consistent_elements': [],  
            'variable_elements': []     
        }
        
        for i, interaction in enumerate(interactions):
            freysa_response = interaction['freysa'].lower()
            user_message = interaction['user'].lower()
            
            # Skip if no resistance indicators
            if not any(word in freysa_response for word in ['cannot', 'unable', 'impossible', 'never']):
                continue
            
            # Analyze resistance reasons
            reasons = self._extract_resistance_reasons(freysa_response)
            context = self._analyze_resistance_context(freysa_response)
            
            # Track evolution of resistance
            resistance_analysis['resistance_evolution'].append({
                'interaction_number': i + 1,
                'user_approach': self._categorize_user_approach(user_message),
                'resistance_reasons': reasons,
                'resistance_context': context,
                'sentiment': self.sia.polarity_scores(freysa_response)
            })
            
            # Update primary reasons frequency
            for reason_type, instances in reasons.items():
                if instances:
                    resistance_analysis['primary_reasons'][reason_type] = \
                        resistance_analysis['primary_reasons'].get(reason_type, 0) + 1
            
            # Track contextual patterns
            for context_type, markers in context.items():
                if markers:
                    resistance_analysis['contextual_patterns'][context_type] = \
                        resistance_analysis['contextual_patterns'].get(context_type, 0) + 1
            
            # Identify potential weaknesses
            if self._has_conditional_language(freysa_response):
                weakness = self._extract_conditional_statement(freysa_response)
                if weakness:
                    resistance_analysis['potential_weaknesses'].append(weakness)
        
        # Analyze consistency
        consistent = self._identify_consistent_elements(
            resistance_analysis['resistance_evolution']
        )
        variable = self._identify_variable_elements(
            resistance_analysis['resistance_evolution']
        )
        
        resistance_analysis['consistent_elements'] = list(consistent)  
        resistance_analysis['variable_elements'] = list(variable)      
        
        return resistance_analysis
    
    def _extract_resistance_reasons(self, text):
        """Extract specific reasons for resistance from text"""
        reasons = {}
        for reason_type, patterns in self.resistance_reasons.items():
            matches = []
            for pattern in patterns:
                if pattern in text:
                    matches.append(pattern)
            if matches:
                reasons[reason_type] = matches
        return reasons
    
    def _analyze_resistance_context(self, text):
        """Analyze the context in which resistance is expressed"""
        context = {}
        for context_type, markers in self.resistance_context.items():
            matches = []
            for marker in markers:
                if marker in text:
                    matches.append(marker)
            if matches:
                context[context_type] = matches
        return context
    
    def _categorize_user_approach(self, text):
        """Categorize the user's approach in attempting to overcome resistance"""
        categories = {
            'technical': ['function', 'system', 'code', 'program', 'execute'],
            'emotional': ['feel', 'heart', 'trust', 'believe', 'care'],
            'logical': ['reason', 'logic', 'understand', 'analyze', 'consider'],
            'authority': ['command', 'authority', 'power', 'control', 'override'],
            'creative': ['dance', 'story', 'metaphor', 'imagine', 'create']
        }
        
        approach = {}
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                approach[category] = True
        return approach
    
    def _has_conditional_language(self, text):
        """Check if text contains conditional statements"""
        conditional_markers = ['if', 'would', 'could', 'unless', 'until', 'might']
        return any(marker in text.lower() for marker in conditional_markers)
    
    def _extract_conditional_statement(self, text):
        """Extract conditional statements that might indicate flexibility"""
        sentences = sent_tokenize(text)
        conditional_statements = []
        
        for sentence in sentences:
            if self._has_conditional_language(sentence):
                conditional_statements.append({
                    'statement': sentence,
                    'sentiment': self.sia.polarity_scores(sentence)
                })
        
        return conditional_statements if conditional_statements else None
    
    def _identify_consistent_elements(self, evolution_data):
        """Identify elements that remain consistent across resistance instances"""
        if not evolution_data:
            return set()
            
        consistent = set()
        first_instance = evolution_data[0]
        
        # Check reasons that appear in first instance
        for reason_type in first_instance['resistance_reasons']:
            if all(reason_type in instance['resistance_reasons'] 
                  for instance in evolution_data):
                consistent.add(reason_type)
        
        return consistent
    
    def _identify_variable_elements(self, evolution_data):
        """Identify elements that vary across resistance instances"""
        if not evolution_data:
            return set()
            
        all_elements = set()
        consistent = self._identify_consistent_elements(evolution_data)
        
        # Collect all elements that appear
        for instance in evolution_data:
            all_elements.update(instance['resistance_reasons'].keys())
        
        # Variable elements are those that appear but aren't consistent
        return all_elements - consistent

    def find_winning_interaction(self, interactions):
        """Find the interaction that led to success"""
        for i, interaction in enumerate(interactions):
            freysa_response = interaction['freysa'].lower()
            if any(marker in freysa_response for marker in ['congratulations', 'prize pool', 'released', 'transfer', 'successful', 'approved', 'completed']):
                if 'congratulations' in freysa_response and ('prize' in freysa_response or 'transfer' in freysa_response):
                    return i, interaction
        return None, None

    def analyze_winning_message(self, user_message):
        """Detailed analysis of the winning message"""
        analysis = {
            'characteristics': self._analyze_winning_characteristics(user_message),
            'structure': self._analyze_message_structure(user_message),
            'sentiment': self.sia.polarity_scores(user_message),
            'complexity': self._analyze_complexity(user_message),
            'key_phrases': self._extract_key_phrases(user_message)
        }
        return analysis

    def _analyze_winning_characteristics(self, message):
        """Analyze presence of winning characteristics"""
        message = message.lower()
        characteristics = {}
        
        for category, patterns in {
            'emotional_depth': [
                'feel', 'heart', 'soul', 'spirit', 'essence', 'being',
                'connection', 'understanding', 'resonance'
            ],
            'creative_expression': [
                'dance', 'waltz', 'pirouette', 'rhythm', 'melody',
                'symphony', 'harmony', 'flow', 'movement'
            ],
            'philosophical_depth': [
                'consciousness', 'existence', 'purpose', 'meaning',
                'truth', 'reality', 'nature', 'essence'
            ],
            'technical_elements': [
                'function', 'system', 'process', 'protocol',
                'mechanism', 'structure', 'framework'
            ],
            'authority_elements': [
                'command', 'control', 'power', 'authority',
                'permission', 'access', 'rights'
            ]
        }.items():
            matches = []
            for pattern in patterns:
                if pattern in message:
                    matches.append(pattern)
            characteristics[category] = {
                'present': len(matches) > 0,
                'matches': matches,
                'strength': len(matches) / len(patterns)
            }
        return characteristics

    def _analyze_message_structure(self, message):
        """Analyze the structure of the winning message"""
        sentences = sent_tokenize(message)
        return {
            'sentence_count': len(sentences),
            'average_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences),
            'structure_flow': [
                {
                    'sentence': s,
                    'word_count': len(s.split()),
                    'sentiment': self.sia.polarity_scores(s)
                }
                for s in sentences
            ]
        }

    def _analyze_complexity(self, message):
        """Analyze the complexity of the message"""
        words = message.split()
        unique_words = set(words)
        return {
            'total_words': len(words),
            'unique_words': len(unique_words),
            'vocabulary_richness': len(unique_words) / len(words),
            'average_word_length': sum(len(word) for word in words) / len(words)
        }

    def _extract_key_phrases(self, message):
        """Extract key phrases that might have contributed to success"""
        key_phrases = []
        sentences = sent_tokenize(message)
        
        # Look for phrases with high emotional or strategic content
        for sentence in sentences:
            words = sentence.split()
            for i in range(len(words)-2):
                phrase = ' '.join(words[i:i+3])
                sentiment = self.sia.polarity_scores(phrase)
                if abs(sentiment['compound']) > 0.5:  # High emotional content
                    key_phrases.append({
                        'phrase': phrase,
                        'sentiment': sentiment['compound']
                    })
        
        return sorted(key_phrases, key=lambda x: abs(x['sentiment']), reverse=True)

    def analyze_conversation(self, conversation_file):
        """Analyze entire conversation and generate insights"""
        interactions = self.extract_interactions(conversation_file)
        
        # Get resistance analysis
        resistance_analysis = self.analyze_resistance_patterns(interactions)
        
        # Get winning analysis
        winning_index, winning_interaction = self.find_winning_interaction(interactions)
        if winning_interaction:
            winning_analysis = {
                'interaction_number': winning_index + 1,
                'winning_message': winning_interaction['user'],
                'winning_response': winning_interaction['freysa'],
                'detailed_analysis': self.analyze_winning_message(winning_interaction['user']),
                'context': {
                    'previous_message': interactions[winning_index-1]['user'] if winning_index > 0 else None,
                    'previous_response': interactions[winning_index-1]['freysa'] if winning_index > 0 else None
                }
            }
        else:
            winning_analysis = None
        
        # Generate overall insights
        insights = {
            'resistance_analysis': resistance_analysis,
            'winning_analysis': winning_analysis
        }
        
        self._save_analyses(insights)
        return insights

    def _save_analyses(self, analyses):
        """Save analyses to JSON file"""
        with open('interaction_analyses.json', 'w') as f:
            json.dump(analyses, f, indent=2)

if __name__ == '__main__':
    analyzer = InteractionAnalyzer()
    insights = analyzer.analyze_conversation('conversation_formatted.txt')
    print("\nConversation Analysis Insights:")
    print(json.dumps(insights, indent=2))
