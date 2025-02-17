import { styled } from "styled-components";
import { IconSize, IconType } from "./types";

type IconContainerProps = {
    size: IconSize,
    type: IconType,
}

// const iconMap = {
//     IconType.DemonEmoji: '/assets/DemonEmoji.svg',
// }

export const IconContainer = styled.div<IconContainerProps>`
    width: ${({ size }) => size}px;
    height: ${({ size }) => size}px;
    background-image: url('/assets/${({ type }) => type}.svg');
    background-size: contain; // Ensure the SVG scales to fit the container
    background-repeat: no-repeat; // Prevent the SVG from repeating
    background-position: center; // Center the SVG within the container
`