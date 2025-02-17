import { keyframes, styled } from "styled-components";

export const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 20px;
  background: ${({ theme }) => theme.color.border.primary};
`;

export const ChatMessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto; // Enable vertical scrolling if content overflows
  padding: 1em;
  word-wrap: break-word; // Ensure long words break and wrap to the next line
  overflow-wrap: break-word; // Ensure long words break and wrap to the next line
  white-space: pre-wrap; // Preserve whitespace and wrap text
`;

export const ChatInputContainer = styled.div``;

// Create a styled input component
export const TerminalInput = styled.input`
  background-color: rgba(0, 0, 0, 0.8); // Transparent black background
  color: white; // White text color
  font-family: 'Courier New', Courier, monospace; // Terminal-esque font
  font-size: 16px; // Font size
  border: none; // Remove default border
  outline: none; // Remove default outline
  padding: 10px; // Padding inside the input
  width: 100%; // Full width
  box-sizing: border-box; // Include padding and border in element's total width and height
  /* caret-color: transparent; // Hide the default caret */
`;

const dotFlashing = keyframes`
  0% {
    opacity: 0.2;
  }
  20% {
    opacity: 1;
  }
  100% {
    opacity: 0.2;
  }
`;

// TODO: Better loading animation one day.
export const LoadingDots = styled.div`
  display: inline-block;
  position: relative;
  width: 80px;
  height: 20px;

  div {
    position: absolute;
    top: 0;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: white;
    animation: ${dotFlashing} 1s infinite ease-in-out both;
  }

  div:nth-child(1) {
    left: 4px;
    animation-delay: -0.32s;
  }

  div:nth-child(2) {
    left: 16px;
    animation-delay: -0.16s;
  }

  div:nth-child(3) {
    left: 28px;
  }
`;