import React, { useState } from 'react';
import { useSendMessage } from './queries/api';

const App: React.FC = () => {
  const [message, setMessage] = useState<string>('');
  
  // Destructuring the result of the mutation hook with proper types
    // @ts-ignore
  const { mutate, isLoading, isError, data, error } = useSendMessage();

  // Handler for input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(e.target.value);
  };

  // Handler for sending the message
  const handleSendMessage = () => {
    mutate(message);
  };

  console.log('isLoading', isLoading);
  console.log('isError', isError);
  console.log('data', data);
  console.log('error', error);

  return (
    <div>
      <h1>🚀 React + TypeScript + Webpack</h1>
      <p>Hello, world!</p>

      <div>
        <input
          type="text"
          value={message}
          onChange={handleInputChange}
          placeholder="Enter your message"
        />
        <button onClick={handleSendMessage} disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send Message'}
        </button>
      </div>

      {/* Handle errors */}
      {isError && <p style={{ color: 'red' }}>Error: {error instanceof Error ? error.message : 'Unknown error'}</p>}

      {/* Display response if available */}
      {data && (
        <div>
          <h3>Response:</h3>
          <pre>{data}</pre>
        </div>
      )}
    </div>
  );
};

export default App;
