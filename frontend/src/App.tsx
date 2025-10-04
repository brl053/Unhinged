import React from 'react';
import { createGlobalStyle, ThemeProvider } from 'styled-components';
import { defaultTheme } from './design_system/theme';
import { RouterProvider } from 'react-router-dom';
import { RouterProviderProps } from 'react-router';

export interface IAppRoutersProps {
  router: RouterProviderProps['router']
}

// TODO: Make this a better pattern one day!
const GlobalStyle = createGlobalStyle`
  body {
    margin: 0;
    padding: 0;
    /* font-family: 'Roboto', sans-serif; */
  }
`;

const App: React.FC<IAppRoutersProps> = ({router}) => {


  return (
    <ThemeProvider theme={defaultTheme}>
      <GlobalStyle /> 
      <RouterProvider router={router}/>
    </ThemeProvider>
  );
};

export default App;
