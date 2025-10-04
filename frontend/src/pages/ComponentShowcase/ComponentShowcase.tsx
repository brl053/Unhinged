import React, { useState, useRef } from 'react';
import { Layout } from '../../../lib/components/Layout/Layout';
import { TextEditor } from '../../../lib/components/TextEditor';
import { EditorInstance, EditorLanguage, EditorTheme, EditorSize } from '../../../lib/components/TextEditor/types';
import {
  ShowcaseContainer,
  ShowcaseSection,
  SectionTitle,
  SectionDescription,
  ControlsContainer,
  ControlGroup,
  ControlLabel,
  Select,
  Button,
  CodeOutput,
  EditorContainer,
  FeatureToggle,
  FeatureLabel
} from './styles';
import { InlineChildren } from '../../../lib/components/InlineChildren/InlineChildren';
import { InlineChildrenAlignment } from '../../../lib/components/InlineChildren/types';

export const ComponentShowcase: React.FC = () => {
  // Editor state
  const [editorValue, setEditorValue] = useState(`// Welcome to the Unhinged Platform Text Editor!
// This is a Monaco Editor wrapped with our custom abstraction

interface User {
  id: string;
  name: string;
  email: string;
}

class UserService {
  private users: User[] = [];

  async createUser(userData: Omit<User, 'id'>): Promise<User> {
    const user: User = {
      id: crypto.randomUUID(),
      ...userData
    };

    this.users.push(user);
    return user;
  }

  async getUserById(id: string): Promise<User | null> {
    return this.users.find(user => user.id === id) || null;
  }

  async getAllUsers(): Promise<User[]> {
    return [...this.users];
  }
}

// Example usage
const userService = new UserService();

async function demo() {
  const newUser = await userService.createUser({
    name: 'Alice Johnson',
    email: 'alice@unhinged.dev'
  });

  console.log('Created user:', newUser);

  const allUsers = await userService.getAllUsers();
  console.log('All users:', allUsers);
}

demo().catch(console.error);`);

  // Editor configuration state
  const [language, setLanguage] = useState<EditorLanguage>('typescript');
  const [theme, setTheme] = useState<EditorTheme>('unhinged-dark');
  const [size, setSize] = useState<EditorSize>('large');
  const [readOnly, setReadOnly] = useState(false);

  // Editor features state
  const [features, setFeatures] = useState({
    lineNumbers: true,
    minimap: true,
    wordWrap: false,
    syntaxHighlighting: true,
    autoComplete: true,
    bracketMatching: true,
    codeFolding: true,
    findReplace: true,
    multiCursor: true,
  });

  // Editor ref
  const editorRef = useRef<EditorInstance>(null);

  // Sample code for different languages
  const sampleCode: Record<EditorLanguage, string> = {
    typescript: `// TypeScript Example
interface ApiResponse<T> = {
  data: T;
  status: number;
  message?: string;
};

async function fetchUser(id: string): Promise<ApiResponse<User>> {
  const response = await fetch(\`/api/users/\${id}\`);
  return response.json();
}`,

    javascript: `// JavaScript Example
function createCounter() {
  let count = 0;

  return {
    increment: () => ++count,
    decrement: () => --count,
    get value() { return count; }
  };
}

const counter = createCounter();
console.log(counter.value); // 0
counter.increment();
console.log(counter.value); // 1`,

    json: `{
  "name": "unhinged-platform",
  "version": "1.0.0",
  "description": "Advanced AI-powered platform",
  "main": "index.js",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "react": "^19.0.0",
    "next": "^14.0.0",
    "styled-components": "^6.0.0"
  }
}`,

    markdown: `# Unhinged Platform Documentation

## Overview

The Unhinged Platform is a cutting-edge AI-powered development environment.

### Features

- **Text Editor**: Monaco-based editor with syntax highlighting
- **Real-time Collaboration**: Multi-user editing capabilities
- **AI Integration**: Built-in AI assistance and code generation
- **Theme System**: Customizable themes and styling

### Getting Started

\`\`\`bash
npm install
npm run dev
\`\`\`

> **Note**: This platform requires Node.js 18+ and modern browser support.`,

    python: `# Python Example
from typing import List, Optional
import asyncio

class UserRepository:
    def __init__(self):
        self._users: List[dict] = []

    async def create_user(self, name: str, email: str) -> dict:
        user = {
            'id': len(self._users) + 1,
            'name': name,
            'email': email
        }
        self._users.append(user)
        return user

    async def find_by_email(self, email: str) -> Optional[dict]:
        return next((u for u in self._users if u['email'] == email), None)

# Usage
async def main():
    repo = UserRepository()
    user = await repo.create_user('Alice', 'alice@example.com')
    print(f"Created: {user}")

if __name__ == '__main__':
    asyncio.run(main())`,

    html: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unhinged Platform</title>
    <style>
        body {
            font-family: 'JetBrains Mono', monospace;
            background: #0d1117;
            color: #e1e4e8;
            margin: 0;
            padding: 2rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Unhinged Platform</h1>
        <p>Advanced AI-powered development environment</p>
    </div>
</body>
</html>`,

    css: `/* Unhinged Platform Styles */
:root {
  --primary-bg: #0d1117;
  --secondary-bg: #161b22;
  --text-primary: #e1e4e8;
  --text-secondary: #8b949e;
  --accent: #58a6ff;
  --border: #30363d;
}

body {
  background: var(--primary-bg);
  color: var(--text-primary);
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  line-height: 1.6;
  margin: 0;
}

.editor-container {
  background: var(--secondary-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.editor-container:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.1);
}`,

    scss: `// Unhinged Platform SCSS
$colors: (
  primary: #0d1117,
  secondary: #161b22,
  accent: #58a6ff,
  text: #e1e4e8,
  border: #30363d
);

@function color($name) {
  @return map-get($colors, $name);
}

@mixin editor-theme($theme: 'dark') {
  @if $theme == 'dark' {
    background: color(primary);
    color: color(text);
    border: 1px solid color(border);
  }
}

.text-editor {
  @include editor-theme();
  border-radius: 8px;
  overflow: hidden;

  &:focus-within {
    border-color: color(accent);
    box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.1);
  }
}`,

    java: `// Java Example
import java.util.*;
import java.util.concurrent.CompletableFuture;

public class UserService {
    private final List<User> users = new ArrayList<>();

    public CompletableFuture<User> createUser(String name, String email) {
        return CompletableFuture.supplyAsync(() -> {
            User user = new User(UUID.randomUUID().toString(), name, email);
            users.add(user);
            return user;
        });
    }

    public Optional<User> findUserById(String id) {
        return users.stream()
            .filter(user -> user.getId().equals(id))
            .findFirst();
    }

    public static class User {
        private final String id;
        private final String name;
        private final String email;

        public User(String id, String name, String email) {
            this.id = id;
            this.name = name;
            this.email = email;
        }

        // Getters...
        public String getId() { return id; }
        public String getName() { return name; }
        public String getEmail() { return email; }
    }
}`,

    kotlin: `// Kotlin Example
import kotlinx.coroutines.*
import java.util.*

data class User(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val email: String
)

class UserRepository {
    private val users = mutableListOf<User>()

    suspend fun createUser(name: String, email: String): User = withContext(Dispatchers.IO) {
        val user = User(name = name, email = email)
        users.add(user)
        user
    }

    suspend fun findByEmail(email: String): User? = withContext(Dispatchers.IO) {
        users.find { it.email == email }
    }

    suspend fun getAllUsers(): List<User> = withContext(Dispatchers.IO) {
        users.toList()
    }
}

// Usage
suspend fun main() {
    val repository = UserRepository()

    val user = repository.createUser("Alice", "alice@unhinged.dev")
    println("Created: $user")

    val found = repository.findByEmail("alice@unhinged.dev")
    println("Found: $found")
}`,

    go: `// Go Example
package main

import (
    "fmt"
    "sync"
    "time"
)

type User struct {
    ID    string \`json:"id"\`
    Name  string \`json:"name"\`
    Email string \`json:"email"\`
}

type UserService struct {
    users []User
    mutex sync.RWMutex
}

func NewUserService() *UserService {
    return &UserService{
        users: make([]User, 0),
    }
}

func (s *UserService) CreateUser(name, email string) User {
    s.mutex.Lock()
    defer s.mutex.Unlock()

    user := User{
        ID:    fmt.Sprintf("user_%d", time.Now().UnixNano()),
        Name:  name,
        Email: email,
    }

    s.users = append(s.users, user)
    return user
}

func (s *UserService) GetAllUsers() []User {
    s.mutex.RLock()
    defer s.mutex.RUnlock()

    result := make([]User, len(s.users))
    copy(result, s.users)
    return result
}

func main() {
    service := NewUserService()

    user := service.CreateUser("Alice", "alice@unhinged.dev")
    fmt.Printf("Created user: %+v\\n", user)

    users := service.GetAllUsers()
    fmt.Printf("All users: %+v\\n", users)
}`,

    rust: `// Rust Example
use std::collections::HashMap;
use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct User {
    pub id: String,
    pub name: String,
    pub email: String,
}

pub struct UserRepository {
    users: HashMap<String, User>,
}

impl UserRepository {
    pub fn new() -> Self {
        Self {
            users: HashMap::new(),
        }
    }

    pub fn create_user(&mut self, name: String, email: String) -> &User {
        let user = User {
            id: Uuid::new_v4().to_string(),
            name,
            email,
        };

        let id = user.id.clone();
        self.users.insert(id.clone(), user);
        self.users.get(&id).unwrap()
    }

    pub fn find_by_email(&self, email: &str) -> Option<&User> {
        self.users.values().find(|user| user.email == email)
    }

    pub fn get_all_users(&self) -> Vec<&User> {
        self.users.values().collect()
    }
}

fn main() {
    let mut repo = UserRepository::new();

    let user = repo.create_user(
        "Alice".to_string(),
        "alice@unhinged.dev".to_string()
    );

    println!("Created user: {:?}", user);

    let found = repo.find_by_email("alice@unhinged.dev");
    println!("Found user: {:?}", found);
}`,

    sql: `-- SQL Example: User Management System
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Insert sample data
INSERT INTO users (name, email) VALUES
    ('Alice Johnson', 'alice@unhinged.dev'),
    ('Bob Smith', 'bob@unhinged.dev'),
    ('Carol Davis', 'carol@unhinged.dev');

-- Query examples
SELECT * FROM users WHERE email LIKE '%unhinged.dev';

SELECT
    COUNT(*) as total_users,
    DATE_TRUNC('day', created_at) as signup_date
FROM users
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY signup_date DESC;

-- Update user
UPDATE users
SET name = 'Alice Johnson-Smith',
    updated_at = CURRENT_TIMESTAMP
WHERE email = 'alice@unhinged.dev';`,

    yaml: `# Unhinged Platform Configuration
name: unhinged-platform
version: 1.0.0
description: Advanced AI-powered development environment

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=http://localhost:8080
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=development
      - DATABASE_URL=postgresql://localhost:5432/unhinged
    volumes:
      - ./backend:/app
    depends_on:
      - database

  database:
    image: postgres:15
    environment:
      - POSTGRES_DB=unhinged
      - POSTGRES_USER=unhinged
      - POSTGRES_PASSWORD=unhinged123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:

networks:
  default:
    name: unhinged-network`,

    xml: `<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">

    <modelVersion>4.0.0</modelVersion>

    <groupId>dev.unhinged</groupId>
    <artifactId>unhinged-platform</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <name>Unhinged Platform</name>
    <description>Advanced AI-powered development environment</description>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <kotlin.version>1.9.0</kotlin.version>
        <ktor.version>2.3.0</ktor.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>io.ktor</groupId>
            <artifactId>ktor-server-core-jvm</artifactId>
            <version>\${ktor.version}</version>
        </dependency>

        <dependency>
            <groupId>io.ktor</groupId>
            <artifactId>ktor-server-netty-jvm</artifactId>
            <version>\${ktor.version}</version>
        </dependency>

        <dependency>
            <groupId>org.jetbrains.kotlin</groupId>
            <artifactId>kotlin-stdlib-jdk8</artifactId>
            <version>\${kotlin.version}</version>
        </dependency>
    </dependencies>

</project>`,

    dockerfile: `# Unhinged Platform Dockerfile
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

# Backend build stage
FROM openjdk:17-jdk-alpine AS backend-builder

WORKDIR /app/backend
COPY backend/build.gradle.kts backend/settings.gradle.kts ./
COPY backend/gradle ./gradle
COPY backend/gradlew ./

RUN ./gradlew dependencies --no-daemon

COPY backend/src ./src
RUN ./gradlew build --no-daemon

# Production stage
FROM openjdk:17-jre-alpine

RUN addgroup -g 1001 -S unhinged && \\
    adduser -S unhinged -u 1001

WORKDIR /app

# Copy backend
COPY --from=backend-builder /app/backend/build/libs/*.jar app.jar

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./public

# Set permissions
RUN chown -R unhinged:unhinged /app
USER unhinged

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["java", "-jar", "app.jar"]`,

    plaintext: `Welcome to the Unhinged Platform Text Editor!

This is a plain text example showing the editor's capabilities
without syntax highlighting.

Features demonstrated:
- Line numbers
- Word wrapping (when enabled)
- Find and replace functionality
- Multi-cursor editing
- Keyboard shortcuts

You can use this editor for:
- Taking notes
- Writing documentation
- Editing configuration files
- Any plain text content

The editor supports many programming languages and file formats,
making it perfect for development work on the Unhinged Platform.

Try switching between different languages using the controls above
to see syntax highlighting in action!`,

    tsx: `// TSX Example - React Component
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

interface User {
  id: string;
  name: string;
  email: string;
}

interface UserListProps {
  users: User[];
  onUserSelect: (user: User) => void;
}

const UserContainer = styled.div\`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: \${({ theme }) => theme.color.background.primary};
  border-radius: 8px;
\`;

const UserCard = styled.div\`
  padding: 1rem;
  background: \${({ theme }) => theme.color.background.secondary};
  border: 1px solid \${({ theme }) => theme.color.border.primary};
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: \${({ theme }) => theme.color.primary.main};
    transform: translateY(-1px);
  }
\`;

export const UserList: React.FC<UserListProps> = ({ users, onUserSelect }) => {
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  useEffect(() => {
    console.log('UserList mounted with', users.length, 'users');
  }, [users]);

  const handleUserClick = (user: User) => {
    setSelectedUser(user);
    onUserSelect(user);
  };

  return (
    <UserContainer>
      <h2>Users ({users.length})</h2>
      {users.map(user => (
        <UserCard
          key={user.id}
          onClick={() => handleUserClick(user)}
          style={{
            borderColor: selectedUser?.id === user.id ? '#58a6ff' : undefined
          }}
        >
          <h3>{user.name}</h3>
          <p>{user.email}</p>
        </UserCard>
      ))}
    </UserContainer>
  );
};`,

    jsx: `// JSX Example - React Component
import React, { useState } from 'react';

const UserForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: ''
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      onSubmit(formData);
      setFormData({ name: '', email: '' });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="user-form">
      <h2>Add New User</h2>

      <div className="form-group">
        <label htmlFor="name">Name:</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className={errors.name ? 'error' : ''}
        />
        {errors.name && <span className="error-message">{errors.name}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className={errors.email ? 'error' : ''}
        />
        {errors.email && <span className="error-message">{errors.email}</span>}
      </div>

      <button type="submit">Add User</button>
    </form>
  );
};

export default UserForm;`
  };

  // Handle language change
  const handleLanguageChange = (newLanguage: EditorLanguage) => {
    setLanguage(newLanguage);
    setEditorValue(sampleCode[newLanguage] || '// Sample code not available');
  };

  // Handle editor change
  const handleEditorChange = (event: any) => {
    setEditorValue(event.value);
  };

  // Handle feature toggle
  const handleFeatureToggle = (feature: keyof typeof features) => {
    setFeatures(prev => ({
      ...prev,
      [feature]: !prev[feature]
    }));
  };

  // Handle editor actions
  const handleFormatCode = () => {
    if (editorRef.current) {
      // Monaco editor format action would be called here
      console.log('Format code action');
    }
  };

  const handleSaveCode = (value: string) => {
    console.log('Save code:', value);
    // Here you would typically save to a file or send to an API
  };

  return (
    <Layout title="Component Showcase">
      <ShowcaseContainer>
        <SectionTitle>🎨 Unhinged Platform Component Showcase</SectionTitle>
        <SectionDescription>
          Explore and test the components available in the Unhinged Platform design system.
          This showcase demonstrates the TextEditor component with full Monaco Editor integration.
        </SectionDescription>

        <ShowcaseSection>
          <h2>Text Editor Component</h2>
          <p>
            A powerful text editor built on Monaco Editor (the same editor that powers VS Code).
            Features syntax highlighting, IntelliSense, and seamless integration with the Unhinged Platform theme system.
          </p>

          <ControlsContainer>
            <ControlGroup>
              <ControlLabel>Language:</ControlLabel>
              <Select
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value as EditorLanguage)}
              >
                <option value="typescript">TypeScript</option>
                <option value="javascript">JavaScript</option>
                <option value="tsx">TSX (React)</option>
                <option value="jsx">JSX (React)</option>
                <option value="json">JSON</option>
                <option value="markdown">Markdown</option>
                <option value="html">HTML</option>
                <option value="css">CSS</option>
                <option value="scss">SCSS</option>
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="kotlin">Kotlin</option>
                <option value="go">Go</option>
                <option value="rust">Rust</option>
                <option value="sql">SQL</option>
                <option value="yaml">YAML</option>
                <option value="xml">XML</option>
                <option value="dockerfile">Dockerfile</option>
                <option value="plaintext">Plain Text</option>
              </Select>
            </ControlGroup>

            <ControlGroup>
              <ControlLabel>Theme:</ControlLabel>
              <Select
                value={theme}
                onChange={(e) => setTheme(e.target.value as EditorTheme)}
              >
                <option value="unhinged-dark">Unhinged Dark</option>
                <option value="unhinged-light">Unhinged Light</option>
                <option value="vs-dark">VS Dark</option>
                <option value="vs-light">VS Light</option>
              </Select>
            </ControlGroup>

            <ControlGroup>
              <ControlLabel>Size:</ControlLabel>
              <Select
                value={size}
                onChange={(e) => setSize(e.target.value as EditorSize)}
              >
                <option value="small">Small (400x200)</option>
                <option value="medium">Medium (600x400)</option>
                <option value="large">Large (800x600)</option>
                <option value="full">Full Size</option>
              </Select>
            </ControlGroup>

            <ControlGroup>
              <FeatureToggle>
                <input
                  type="checkbox"
                  id="readOnly"
                  checked={readOnly}
                  onChange={(e) => setReadOnly(e.target.checked)}
                />
                <FeatureLabel htmlFor="readOnly">Read Only</FeatureLabel>
              </FeatureToggle>
            </ControlGroup>
          </ControlsContainer>

          <h3>Editor Features</h3>
          <ControlsContainer>
            {Object.entries(features).map(([feature, enabled]) => (
              <ControlGroup key={feature}>
                <FeatureToggle>
                  <input
                    type="checkbox"
                    id={feature}
                    checked={enabled}
                    onChange={() => handleFeatureToggle(feature as keyof typeof features)}
                  />
                  <FeatureLabel htmlFor={feature}>
                    {feature.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                  </FeatureLabel>
                </FeatureToggle>
              </ControlGroup>
            ))}
          </ControlsContainer>

          <InlineChildren alignment={InlineChildrenAlignment.Center}>
            <Button onClick={handleFormatCode}>Format Code</Button>
            <Button onClick={() => handleSaveCode(editorValue)}>Save Code</Button>
            <Button onClick={() => editorRef.current?.focus()}>Focus Editor</Button>
          </InlineChildren>

          <EditorContainer>
            <TextEditor
              ref={editorRef}
              value={editorValue}
              language={language}
              theme={theme}
              size={size}
              readOnly={readOnly}
              features={features}
              onChange={handleEditorChange}
              onSave={handleSaveCode}
              placeholder="Start typing your code here..."
              testId="showcase-editor"
            />
          </EditorContainer>

          <h3>Current Editor Value</h3>
          <CodeOutput>
            <pre>{editorValue}</pre>
          </CodeOutput>
        </ShowcaseSection>

        <ShowcaseSection>
          <h2>Integration Examples</h2>
          <p>
            The TextEditor component is designed to integrate seamlessly with the Unhinged Platform.
            Here are some common usage patterns:
          </p>

          <h3>Basic Usage</h3>
          <CodeOutput>
            <pre>{`import { TextEditor } from '@/lib/components/TextEditor';

function MyCodeEditor() {
  const [code, setCode] = useState('console.log("Hello World");');

  return (
    <TextEditor
      value={code}
      language="typescript"
      theme="unhinged-dark"
      onChange={(e) => setCode(e.value)}
      onSave={(value) => console.log('Saved:', value)}
    />
  );
}`}</pre>
          </CodeOutput>

          <h3>Advanced Configuration</h3>
          <CodeOutput>
            <pre>{`<TextEditor
  value={code}
  language="typescript"
  theme="unhinged-dark"
  size="large"
  features={{
    lineNumbers: true,
    minimap: true,
    wordWrap: false,
    syntaxHighlighting: true,
    autoComplete: true,
    bracketMatching: true,
    codeFolding: true,
    findReplace: true,
    multiCursor: true,
  }}
  onChange={handleChange}
  onMount={(editor) => console.log('Editor mounted:', editor)}
  onSave={handleSave}
  placeholder="Enter your code here..."
/>`}</pre>
          </CodeOutput>
        </ShowcaseSection>
      </ShowcaseContainer>
    </Layout>
  );
};