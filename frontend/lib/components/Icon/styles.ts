import { styled } from "styled-components";
import { IconSize, IconType } from "./types";

type IconContainerProps = {
    size: number,
    type: IconType,
}

type FallbackIconProps = {
    size: number;
}

export const IconContainer = styled.div<IconContainerProps>`
    width: ${({ size }) => size}px;
    height: ${({ size }) => size}px;
    background-image: url('/assets/${({ type }) => type}.svg');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    flex-shrink: 0;
`;

export const FallbackIcon = styled.div<FallbackIconProps>`
    width: ${({ size }) => size}px;
    height: ${({ size }) => size}px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: ${({ size }) => Math.max(12, size * 0.7)}px;
    color: currentColor;
    flex-shrink: 0;
    user-select: none;
`;