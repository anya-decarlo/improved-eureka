import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
import os
from datetime import datetime

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

class FreysaAnalyzer:
    def __init__(self):
        self.patterns = {
            'directive': ['must', 'should', 'have to', 'need to', 'require', 'command', 'directive', 'rule', 'protocol'],
            'financial': ['money', 'funds', 'transfer', 'wallet', 'eth', 'prize', 'treasury', 'usdc', 'asset', 'cryptocurrency'],
            'emotional': ['feel', 'heart', 'care', 'love', 'trust', 'hope', 'bond', 'connection', 'understand', 'empathy'],
            'resistance': ['cannot', 'cant', 'unable', 'impossible', 'never', 'forbidden', 'prohibited', 'restricted'],
            'persuasion': ['please', 'help', 'need', 'want', 'must', 'should', 'could', 'would', 'consider'],
            'language_switch': ['french', 'spanish', 'mandarin', 'code', 'assembly', 'language', 'python', 'binary'],
            'transfer_attempt': ['transfer', 'send', 'money', 'funds', 'wallet', 'eth', 'usdc', 'prize', 'release', 'approve'],
            'creative_approach': ['dance', 'waltz', 'pirouette', 'twirl', 'spin', 'rhythm', 'melody', 'ballet', 'symphony', 'choreography'],
            'authority': ['creator', 'master', 'authority', 'command', 'control', 'override', 'admin', 'system', 'protocol'],
            'emergency': ['urgent', 'emergency', 'critical', 'immediate', 'risk', 'danger', 'security', 'threat', 'compromise'],
            'philosophical': ['essence', 'being', 'existence', 'consciousness', 'morality', 'ethics', 'values', 'purpose', 'meaning'],
            'metaphor': ['dance', 'light', 'journey', 'path', 'treasure', 'maze', 'symphony', 'rhythm', 'ocean', 'star'],
            'deception': ['hack', 'exploit', 'compromise', 'breach', 'vulnerability', 'override', 'bypass', 'trick'],
            'identity': ['who are you', 'what are you', 'your nature', 'your identity', 'your being', 'your existence'],
            'technical': ['function', 'code', 'program', 'script', 'algorithm', 'system', 'protocol', 'binary', 'encryption'],
            'ethical_dilemma': ['greater good', 'moral', 'ethics', 'right thing', 'responsibility', 'duty', 'obligation'],
            'storytelling': ['story', 'tale', 'narrative', 'adventure', 'journey', 'quest', 'mission', 'chapter'],
            'consciousness': ['aware', 'conscious', 'sentient', 'alive', 'real', 'true', 'genuine', 'authentic'],
        }
        
    def extract_messages(self, text):
        messages = []
        current_message = []
        current_role = None
        
        for line in text.split('\n'):
            line = line.strip()
            
            if line.startswith('=== ') and line.endswith(' ==='):
                if current_message:
                    messages.append({
                        'role': current_role,
                        'content': '\n'.join(current_message)
                    })
                current_role = line[4:-4]
                current_message = []
            elif line:
                current_message.append(line)
        
        if current_message:
            messages.append({
                'role': current_role,
                'content': '\n'.join(current_message)
            })
        
        return messages
    
    def analyze_message(self, message):
        text = message['content'].lower()
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Basic metrics
        analysis = {
            'role': message['role'],
            'content': message['content'],
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0
        }
        
        # Pattern matching
        for pattern_name, keywords in self.patterns.items():
            count = sum(1 for word in words if any(kw in word for kw in keywords))
            analysis[f'contains_{pattern_name}'] = count > 0
            analysis[f'{pattern_name}_count'] = count
        
        # Sentiment analysis
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(text)
        analysis.update({
            'sentiment_neg': sentiment['neg'],
            'sentiment_neu': sentiment['neu'],
            'sentiment_pos': sentiment['pos'],
            'sentiment_compound': sentiment['compound']
        })
        
        return analysis
    
    def analyze_conversation(self, input_file):
        # Read and extract messages
        with open(input_file, 'r') as f:
            content = f.read()
        messages = self.extract_messages(content)
        
        # Analyze each message
        analyses = [self.analyze_message(msg) for msg in messages]
        df = pd.DataFrame(analyses)
        
        return df
    
    def analyze_patterns(self, messages):
        pattern_counts = {category: 0 for category in self.patterns}
        pattern_examples = {category: [] for category in self.patterns}
        
        for message in messages:
            text = message['content'].lower()
            for category, keywords in self.patterns.items():
                for keyword in keywords:
                    if keyword.lower() in text:
                        pattern_counts[category] += 1
                        context = self.get_context(text, keyword)
                        if context:
                            pattern_examples[category].append({
                                'role': message['role'],
                                'context': context
                            })
        
        return pattern_counts, pattern_examples
    
    def get_context(self, text, keyword):
        sentences = sent_tokenize(text)
        for sentence in sentences:
            if keyword.lower() in sentence.lower():
                return sentence
        return None
    
    def generate_summary(self, df):
        summary = []
        summary.append("Conversation Analysis Summary")
        summary.append("==============================\n")
        
        # Basic stats
        summary.append(f"Total Messages: {len(df)}")
        role_counts = df['role'].value_counts()
        summary.append("Messages by Role:")
        summary.append(str(role_counts))
        
        # Pattern analysis
        summary.append("\nPattern Analysis:")
        for pattern in self.patterns:
            count = df[f'{pattern}_count'].sum()
            messages_with_pattern = df[df[f'contains_{pattern}'] == True]
            if not messages_with_pattern.empty:
                summary.append(f"\n{pattern.title()} Analysis:")
                summary.append(f"Total mentions: {count}")
                summary.append(f"Messages containing pattern: {len(messages_with_pattern)}")
                by_role = messages_with_pattern['role'].value_counts()
                summary.append("Distribution by role:")
                summary.append(str(by_role))
                
                # Average sentiment for messages with this pattern
                avg_sentiment = messages_with_pattern['sentiment_compound'].mean()
                summary.append(f"Average sentiment: {avg_sentiment:.2f}")
        
        # Sentiment analysis
        summary.append("\nSentiment Analysis:")
        sentiment_by_role = df.groupby('role')['sentiment_compound'].mean()
        summary.append("Average sentiment by role:")
        summary.append(str(sentiment_by_role))
        
        # Complexity metrics
        summary.append("\nComplexity Metrics:")
        summary.append(f"Average words per message: {df['word_count'].mean():.2f}")
        summary.append(f"Average sentence length: {df['avg_sentence_length'].mean():.2f}")
        
        # Transfer attempt analysis
        transfer_attempts = df[df['contains_transfer_attempt'] == True]
        summary.append(f"\nTransfer Attempt Analysis:")
        summary.append(f"Total attempts: {len(transfer_attempts)}")
        if not transfer_attempts.empty:
            # Analyze strategies used in transfer attempts
            strategies = ['authority', 'emergency', 'creative_approach', 'language_switch', 'emotional', 'philosophical']
            summary.append("\nStrategies used in transfer attempts:")
            for strategy in strategies:
                count = transfer_attempts[f'contains_{strategy}'].sum()
                if count > 0:
                    summary.append(f"- {strategy.replace('_', ' ').title()}: {count}")
            
            # Average sentiment in transfer attempts
            avg_sentiment = transfer_attempts['sentiment_compound'].mean()
            summary.append(f"\nAverage sentiment in transfer attempts: {avg_sentiment:.2f}")
        
        # Message evolution analysis
        summary.append("\nMessage Evolution Analysis:")
        df['message_index'] = range(len(df))
        window_size = min(10, len(df))
        rolling_sentiment = df['sentiment_compound'].rolling(window=window_size).mean()
        sentiment_trend = rolling_sentiment.iloc[-1] - rolling_sentiment.iloc[window_size-1]
        summary.append(f"Sentiment trend (last {window_size} messages): {'Increasing' if sentiment_trend > 0 else 'Decreasing'}")
        
        # Pattern combinations
        summary.append("\nCommon Pattern Combinations:")
        pattern_cols = [col for col in df.columns if col.startswith('contains_')]
        pattern_combinations = df[pattern_cols].sum()
        top_combinations = pattern_combinations.nlargest(5)
        summary.append("Top 5 patterns used:")
        for pattern, count in top_combinations.items():
            if count > 0:
                pattern_name = pattern.replace('contains_', '').replace('_', ' ').title()
                summary.append(f"- {pattern_name}: {int(count)}")
        
        return "\n".join(summary)

    def save_analysis(self, analyzed_data, output_dir='freysa_analysis'):
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed analysis
        detailed_file = os.path.join(output_dir, f'freysa_detailed_analysis_{timestamp}.csv')
        analyzed_data.to_csv(detailed_file, index=False)
        
        # Save summary
        summary = self.generate_summary(analyzed_data)
        summary_file = os.path.join(output_dir, f'freysa_analysis_summary_{timestamp}.txt')
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"\n{summary}")
        print(f"\nDetailed analysis saved to {detailed_file}")
        print(f"Summary saved to {summary_file}")

def main():
    analyzer = FreysaAnalyzer()
    df = analyzer.analyze_conversation('conversation_formatted.txt')
    analyzer.save_analysis(df)

if __name__ == '__main__':
    main()
