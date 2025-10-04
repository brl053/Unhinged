/**
 * @fileoverview InlineChildren Component
 * @purpose Flexible inline layout component for arranging child elements
 * @editable true - LLM should update when adding new layout features
 * @deprecated false
 *
 * @remarks
 * Provides a simple way to arrange child elements in a row with configurable
 * spacing, alignment, and justification. Uses transient props to avoid DOM warnings.
 */

import { PropsWithChildren } from "react";
import { InlineChildrenContainer } from "./styles";
import { InlineChildrenAlignment, InlineChildrenJustification, InlineChildrenSize } from "./types";

export type InlineChildrenProps = {
    size?: InlineChildrenSize
    justification?: InlineChildrenJustification,
    alignment?: InlineChildrenAlignment,
} & PropsWithChildren

export const InlineChildren: React.FC<InlineChildrenProps> = ({ size, justification, alignment, children }) => {

    return <InlineChildrenContainer $size={size} $justification={justification} $alignment={alignment}>
        {children}
    </InlineChildrenContainer>
}