import React from 'react';
import { IconContainer, FallbackIcon } from "./styles";
import { IconSize, IconType } from "./types";

export type IconProps = {
    type: IconType;
    size: IconSize | 'sm' | 'md' | 'lg';
    className?: string;
}

export const Icon: React.FC<IconProps> = ({ type, size, className }) => {
    // Convert string sizes to pixel values
    const getPixelSize = (size: IconSize | 'sm' | 'md' | 'lg'): number => {
        if (typeof size === 'number') return size;

        switch (size) {
            case 'sm': return IconSize.Small;
            case 'md': return IconSize.Medium;
            case 'lg': return IconSize.Large;
            default: return IconSize.Medium;
        }
    };

    const pixelSize = getPixelSize(size);

    // For icons that don't have SVG files, render fallback
    const renderFallbackIcon = () => {
        switch (type) {
            case IconType.Menu:
                return <FallbackIcon size={pixelSize}>☰</FallbackIcon>;
            case IconType.Close:
                return <FallbackIcon size={pixelSize}>✕</FallbackIcon>;
            case IconType.ChevronLeft:
                return <FallbackIcon size={pixelSize}>‹</FallbackIcon>;
            case IconType.ChevronRight:
                return <FallbackIcon size={pixelSize}>›</FallbackIcon>;
            case IconType.ChevronUp:
                return <FallbackIcon size={pixelSize}>^</FallbackIcon>;
            case IconType.ChevronDown:
                return <FallbackIcon size={pixelSize}>v</FallbackIcon>;
            case IconType.Settings:
                return <FallbackIcon size={pixelSize}>⚙</FallbackIcon>;
            case IconType.User:
                return <FallbackIcon size={pixelSize}>👤</FallbackIcon>;
            case IconType.Home:
                return <FallbackIcon size={pixelSize}>🏠</FallbackIcon>;
            case IconType.Search:
                return <FallbackIcon size={pixelSize}>🔍</FallbackIcon>;
            case IconType.Plus:
                return <FallbackIcon size={pixelSize}>+</FallbackIcon>;
            case IconType.Edit:
                return <FallbackIcon size={pixelSize}>✏</FallbackIcon>;
            case IconType.Delete:
                return <FallbackIcon size={pixelSize}>🗑</FallbackIcon>;
            case IconType.Save:
                return <FallbackIcon size={pixelSize}>💾</FallbackIcon>;
            default:
                return <IconContainer type={type} size={pixelSize} className={className} />;
        }
    };

    return renderFallbackIcon();
}