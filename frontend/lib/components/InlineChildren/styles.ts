/**
 * @fileoverview InlineChildren Component Styles
 * @purpose Styled components for flexible inline layout component
 * @editable true - LLM should update styles when adding new layout features
 * @deprecated false
 *
 * @remarks
 * Uses transient props ($prop) to prevent styled-components from passing
 * custom props to the DOM element, which would trigger React warnings.
 */

import { styled } from "styled-components";
import { InlineChildrenAlignment, InlineChildrenJustification, InlineChildrenSize } from "./types";

interface InlineChildrenContainerProps {
    $size?: InlineChildrenSize;
    $justification?: InlineChildrenJustification;
    $alignment?: InlineChildrenAlignment;
}

export const InlineChildrenContainer = styled.div<InlineChildrenContainerProps>`
    display: flex;
    flex-direction: row;
    ${({ $size }) => $size !== undefined && `gap: ${$size}px;`}
    ${({ $justification }) => $justification && `justify-content: ${$justification};`}
    ${({ $alignment }) => $alignment && `align-items: ${$alignment};`}
`