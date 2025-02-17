import { styled } from "styled-components";

export const LayoutContainer = styled.div`
    display: grid;
    grid-template-rows: 65px 1fr;
    grid-template-columns: auto 1fr;
    grid-template-areas: 
        "header header"
        "sidenav main";
    height: 100vh;
    width: 100vw;
    background: ${({ theme }) => theme.color.background.primary};
    color: ${({ theme }) => theme.color.text.primary};
`;

export const LayoutHeader = styled.header`
    grid-area: header;
    background: ${({ theme }) => theme.color.background.secondary};
    padding: 1em;
    border-bottom: 1px solid ${({ theme }) => theme.color.border.secondary};

`;

export const LayoutSideNavContainer = styled.nav`
    grid-area: sidenav;
    background: ${({ theme }) => theme.color.background.secondary};
    padding: 0.5em;
    border-right: 1px solid ${({ theme }) => theme.color.border.secondary};

`;

export const LayoutMainContainer = styled.main`
    grid-area: main;
    padding: 2em;
    overflow-y: auto;

`;