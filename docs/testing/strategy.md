# 🧪 Testing Strategy

## Overview

Unhinged follows a comprehensive testing strategy with multiple layers of testing to ensure reliability and maintainability.

## Testing Pyramid

```
    🔺 E2E Tests (Playwright)
   🔺🔺 Integration Tests  
  🔺🔺🔺 Unit Tests
```

### 🎯 **Unit Tests**
**Fast, isolated, focused**

#### Backend (Kotlin/JUnit)
```kotlin
@Test
fun `should generate contextual response`() {
    val domainService = ChatDomainService()
    val history = listOf(
        ChatMessage("1", "Hello", MessageRole.USER, "2025-01-05T10:00:00Z", "session-1")
    )
    
    val response = domainService.generateContextualResponse("How are you?", history)
    
    assertThat(response).isNotEmpty()
    assertThat(response).contains("Hello")
}
```

#### Frontend (Jest/React Testing Library)
```typescript
import { render, screen } from '@testing-library/react';
import { Chatroom } from './Chatroom';

test('renders chat interface', () => {
  render(<Chatroom />);
  expect(screen.getByRole('textbox')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
});
```

### 🎯 **Integration Tests**
**Test layer interactions**

#### Backend API Tests
```kotlin
@Test
fun `should create session and send message`() {
    val session = chatUseCases.createSession(CreateSessionRequest("user-1", "Test"))
    val response = chatUseCases.sendMessage(
        SendMessageRequest("Hello", session.id, "user-1")
    )
    
    assertThat(response.assistantMessage.content).isNotEmpty()
    assertThat(response.sessionId).isEqualTo(session.id)
}
```

#### Frontend Service Tests
```typescript
import { chatService } from '../services/ChatService';

test('ChatService sends message successfully', async () => {
  const response = await chatService.sendMessage({
    prompt: 'Test message',
    userId: 'test-user'
  });
  
  expect(response.response).toBeDefined();
  expect(response.sessionId).toBeDefined();
});
```

### 🎯 **E2E Tests (Playwright)**
**Full user journeys**

```typescript
test('User can have a conversation', async ({ page }) => {
  await page.goto('/');
  
  await page.fill('[data-testid="message-input"]', 'Hello!');
  await page.click('[data-testid="send-button"]');
  
  await expect(page.locator('[data-testid="message"]')).toContainText('Hello!');
  await expect(page.locator('[data-testid="response"]')).toBeVisible();
});
```

## Test Categories

### 🔥 **Smoke Tests**
**Critical functionality verification**

- ✅ Application loads
- ✅ Backend API responds
- ✅ Chat functionality works
- ✅ No critical errors

**Run with:** `npm run test:smoke`

### 🧪 **Regression Tests**
**Prevent breaking changes**

- ✅ All existing features work
- ✅ API contracts maintained
- ✅ UI components render correctly

### 🚀 **Performance Tests**
**Ensure acceptable performance**

- ✅ Page load times < 3 seconds
- ✅ API response times < 500ms
- ✅ Memory usage within limits

### ♿ **Accessibility Tests**
**Ensure inclusive design**

- ✅ Keyboard navigation
- ✅ Screen reader compatibility
- ✅ Color contrast ratios
- ✅ ARIA labels

## Running Tests

### Backend Tests
```bash
cd backend
./gradlew test                    # All tests
./gradlew test --tests "*Unit*"  # Unit tests only
./gradlew test --tests "*Integration*" # Integration tests only
```

### Frontend Tests
```bash
cd frontend
npm test                         # Jest unit tests
npm run test:smoke              # Playwright smoke tests
npm run test:headed             # Playwright with browser UI
npm run test:ui                 # Playwright test runner UI
```

### Full Test Suite
```bash
make test                       # Run all tests
make test-unit                  # Unit tests only
make test-integration          # Integration tests only
make test-e2e                  # E2E tests only
```

## Test Data Management

### Test Fixtures
```typescript
// tests/fixtures/chatData.ts
export const mockChatSession = {
  sessionId: 'test-session-123',
  userId: 'test-user',
  title: 'Test Session',
  createdAt: '2025-01-05T10:00:00Z',
  isActive: true
};

export const mockMessages = [
  {
    id: 'msg-1',
    content: 'Hello!',
    role: 'user' as const,
    timestamp: '2025-01-05T10:00:00Z'
  }
];
```

### Database Seeding
```kotlin
@TestConfiguration
class TestDataConfiguration {
    
    @Bean
    @Primary
    fun testChatRepository(): ChatMessageRepository {
        return InMemoryChatMessageRepository().apply {
            // Seed with test data
        }
    }
}
```

## Continuous Integration

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-java@v3
        with:
          java-version: '17'
      - run: cd backend && ./gradlew test

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm ci && npm test

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: docker-compose up -d
      - run: cd frontend && npx playwright test
```

## Test Coverage

### Coverage Targets
- **Unit Tests**: > 80% line coverage
- **Integration Tests**: > 70% feature coverage
- **E2E Tests**: > 90% critical path coverage

### Coverage Reports
```bash
# Backend coverage
cd backend && ./gradlew jacocoTestReport

# Frontend coverage
cd frontend && npm test -- --coverage

# View reports
open backend/build/reports/jacoco/test/html/index.html
open frontend/coverage/lcov-report/index.html
```

## Best Practices

### ✅ **Do**
- Write tests before fixing bugs
- Use descriptive test names
- Test behavior, not implementation
- Keep tests independent
- Use appropriate test doubles
- Test edge cases and error conditions

### ❌ **Don't**
- Test implementation details
- Write flaky tests
- Ignore failing tests
- Over-mock dependencies
- Write tests that depend on external services
- Skip testing error paths

## Test Debugging

### Playwright Debugging
```bash
# Run with browser UI
npm run test:headed

# Run with Playwright Inspector
npx playwright test --debug

# Generate test code
npx playwright codegen localhost:8081
```

### Backend Debugging
```bash
# Run tests with debug output
./gradlew test --debug-jvm

# Run specific test with logging
./gradlew test --tests "ChatUseCasesTest" --info
```

## Test Maintenance

### Regular Tasks
- ✅ Update test data when schemas change
- ✅ Review and update test coverage
- ✅ Remove obsolete tests
- ✅ Update test dependencies
- ✅ Monitor test execution times

### Test Refactoring
- Extract common test utilities
- Use page object models for E2E tests
- Create reusable test fixtures
- Standardize assertion patterns
