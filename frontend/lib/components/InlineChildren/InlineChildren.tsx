import { PropsWithChildren } from "react";
import { InlineChildrenContainer } from "./styles";
import { InlineChildrenAlignment, InlineChildrenJustification, InlineChildrenSize } from "./types";

export type InlineChildrenProps = {
    size?: InlineChildrenSize
    justification?: InlineChildrenJustification,
    alignment?: InlineChildrenAlignment,
} & PropsWithChildren

export const InlineChildren: React.FC<InlineChildrenProps> = ({ size, justification, alignment, children }) => {

    return <InlineChildrenContainer size={size} justification={justification} alignment={alignment}>
        {children}
    </InlineChildrenContainer>
}