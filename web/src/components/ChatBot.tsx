/**
 * Interactive chatbot widget for asking questions about course content.
 */

import React, { useState, useRef, useEffect } from 'react';
import { api, ChatQueryResponse, ChatSource } from '../services/api';
import { useAuth } from '../context/AuthContext';
import styles from './ChatBot.module.css';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  sources?: ChatSource[];
  followUps?: string[];
}

interface ChatBotProps {
  defaultDifficulty?: 'beginner' | 'intermediate' | 'advanced';
}

export const ChatBot: React.FC<ChatBotProps> = ({ defaultDifficulty = 'beginner' }) => {
  const { user, isAuthenticated } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: 'Hello! I\'m your AI tutor. Ask me anything about the course materials. What would you like to learn?',
      followUps: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState<'beginner' | 'intermediate' | 'advanced'>(
    defaultDifficulty
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (query: string = input) => {
    if (!query.trim() || !isAuthenticated) return;

    setError(null);
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: query,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.askQuestion({
        query,
        user_difficulty: selectedDifficulty,
      });

      const botMessage: Message = {
        id: response.message_id,
        type: 'bot',
        content: response.response,
        sources: response.sources,
        followUps: response.follow_up_options,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to get response. Please try again.';
      setError(errorMessage);

      const errorBotMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'bot',
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
      };

      setMessages((prev) => [...prev, errorBotMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollowUp = (followUp: string) => {
    handleSendMessage(followUp);
  };

  if (!isAuthenticated) {
    return (
      <div className={styles.chatbotContainer}>
        <div className={styles.authPrompt}>
          <h3>Sign in to chat with the AI tutor</h3>
          <p>You need to be logged in to ask questions and get personalized answers.</p>
          <a href="/auth/login" className={styles.loginButton}>
            Sign In
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.chatbotContainer}>
      <div className={styles.header}>
        <h2>AI Tutor</h2>
        <div className={styles.difficultySelector}>
          <label>Level:</label>
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value as any)}
            disabled={isLoading}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
      </div>

      <div className={styles.messagesContainer}>
        {messages.map((message) => (
          <div key={message.id} className={`${styles.message} ${styles[message.type]}`}>
            <div className={styles.messageContent}>{message.content}</div>

            {message.sources && message.sources.length > 0 && (
              <div className={styles.sources}>
                <details>
                  <summary>📚 {message.sources.length} source(s)</summary>
                  <ul>
                    {message.sources.map((source) => (
                      <li key={source.chapter_id}>
                        <strong>{source.chapter_title}</strong> ({source.module_slug})
                        <br />
                        <small>{source.excerpt}</small>
                        <br />
                        <span className={styles.relevance}>Relevance: {(source.relevance_score * 100).toFixed(0)}%</span>
                      </li>
                    ))}
                  </ul>
                </details>
              </div>
            )}

            {message.followUps && message.followUps.length > 0 && (
              <div className={styles.followUps}>
                <p className={styles.followUpLabel}>Follow-up questions:</p>
                <div className={styles.followUpButtons}>
                  {message.followUps.map((followUp, idx) => (
                    <button
                      key={idx}
                      className={styles.followUpButton}
                      onClick={() => handleFollowUp(followUp)}
                      disabled={isLoading}
                    >
                      {followUp}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className={`${styles.message} ${styles.bot}`}>
            <div className={styles.typing}>
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className={styles.errorBanner}>
          <button className={styles.closeError} onClick={() => setError(null)}>
            ✕
          </button>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className={styles.inputContainer}>
        <input
          type="text"
          placeholder="Ask your question... (or press Enter)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !isLoading) {
              handleSendMessage();
            }
          }}
          disabled={isLoading}
          className={styles.input}
        />
        <button
          onClick={() => handleSendMessage()}
          disabled={!input.trim() || isLoading}
          className={styles.sendButton}
        >
          {isLoading ? '⏳' : '→'}
        </button>
      </div>
    </div>
  );
};

export default ChatBot;
