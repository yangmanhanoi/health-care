import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { apiService } from '../services/api';
import { toast } from 'sonner';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

interface ChatState {
  step: number;
  symptoms: number[];
  model_type: string;
  question?: string;
}

const MODEL_OPTIONS = [
  { value: 'rnn', label: 'RNN (Recommended)' },
  { value: 'cnn', label: 'CNN' },
  { value: 'fcnn', label: 'Fully Connected NN' },
  { value: 'rf', label: 'Random Forest' },
];

export const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatState, setChatState] = useState<ChatState>({
    step: -1,
    symptoms: [],
    model_type: 'rnn',
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (type: 'user' | 'bot', content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    addMessage('user', userMessage);
    setIsLoading(true);

    try {
      const response = await apiService.sendChatMessage({
        message: userMessage,
        step: chatState.step,
        symptoms: chatState.symptoms,
        model_type: chatState.model_type,
      });

      addMessage('bot', response.response);
      setChatState({
        step: response.step,
        symptoms: response.symptoms,
        model_type: response.model_type,
        question: response.question,
      });
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message. Please try again.');
      addMessage('bot', 'Sorry, I encountered an error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const resetChat = () => {
    setMessages([]);
    setChatState({
      step: -1,
      symptoms: [],
      model_type: chatState.model_type,
    });
    addMessage('bot', 'Hello! I\'m your AI health assistant. Type "start" to begin the symptom checker.');
  };

  const startChat = () => {
    setInputValue('start');
    handleSendMessage();
  };

  useEffect(() => {
    // Initialize chat with welcome message
    addMessage('bot', 'Hello! I\'m your AI health assistant. Type "start" to begin the symptom checker.');
  }, []);

  const formatMessage = (content: string) => {
    // Split by newlines and render each line
    return content.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto p-4">
      <Card className="flex-1 flex flex-col">
        <CardHeader className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-6 w-6 text-blue-600" />
              AI Health Assistant
            </CardTitle>
            <div className="flex items-center gap-2">
              <Select
                value={chatState.model_type}
                onValueChange={(value) => setChatState(prev => ({ ...prev, model_type: value }))}
              >
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {MODEL_OPTIONS.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm" onClick={resetChat}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">
              Model: {MODEL_OPTIONS.find(m => m.value === chatState.model_type)?.label}
            </Badge>
            <Badge variant="outline">
              Step: {chatState.step === -1 ? 'Ready' : chatState.step}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="flex-1 flex flex-col min-h-0">
          <ScrollArea className="flex-1 pr-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex items-start gap-3 ${
                    message.type === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.type === 'bot' && (
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <Bot className="h-4 w-4 text-blue-600" />
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="text-sm whitespace-pre-wrap">
                      {formatMessage(message.content)}
                    </div>
                    <div className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                  {message.type === 'user' && (
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <User className="h-4 w-4 text-white" />
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Bot className="h-4 w-4 text-blue-600" />
                  </div>
                  <div className="bg-gray-100 rounded-lg px-4 py-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          <div className="flex-shrink-0 mt-4">
            {messages.length === 1 && (
              <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800 mb-2">
                  Quick start: Click the button below to begin the symptom checker
                </p>
                <Button onClick={startChat} className="w-full">
                  Start Symptom Checker
                </Button>
              </div>
            )}
            
            <div className="flex gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  chatState.question 
                    ? `Answer: ${chatState.question} (Y/N)`
                    : "Type your message..."
                }
                disabled={isLoading}
                className="flex-1"
              />
              <Button 
                onClick={handleSendMessage} 
                disabled={!inputValue.trim() || isLoading}
                size="icon"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            
            {chatState.step >= 1 && chatState.step <= 20 && (
              <div className="mt-2 flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setInputValue('y')}
                  disabled={isLoading}
                >
                  Yes
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setInputValue('n')}
                  disabled={isLoading}
                >
                  No
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
