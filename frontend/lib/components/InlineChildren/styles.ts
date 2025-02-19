import { styled } from "styled-components";
import { InlineChildrenAlignment, InlineChildrenJustification, InlineChildrenSize } from "./types";
import { InlineChildrenProps } from "./InlineChildren";

export const InlineChildrenContainer = styled.div<InlineChildrenProps>`
    display: flex;
    flex-direction: row;
    ${({ size }) => size !== undefined && `gap: ${size}px;`}
    ${({ justification }) => justification && `justify-content: ${justification};`}
    ${({ alignment }) => alignment && `align-items: ${alignment};`}
`