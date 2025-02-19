
enum ThemeName {
    BASIC = 'Basic Theme',
}

export const basicTheme: Theme = {
    name: ThemeName.BASIC,
    color: {
      palette: {
        white: '#ffffff',
      },
      text: {
        primary: '#ffffff',
        secondary: '#000000',
      },
      background: {
        primary: '#562b70',
        secondary: '#8550a6',
        hovered: '#f0f0f0',
      },
      border: {
        primary: '#301442',
        secondary: '#ffffff'
      },

    },
    fonts: {
      main: 'Arial, sans-serif',
      heading: 'Roboto, sans-serif',
    },
  };


type Theme = {
    name: ThemeName;
    color : {
      palette: {
        white: string;
      }
      background: {
        primary: string;
        secondary: string;
        hovered: string;
      },
      border: {
        primary: string;
        secondary: string;
      }
      text: {
        primary: string;
        secondary: string;
      }
    };
    fonts: {
      main: string;
      heading: string;
    };
}