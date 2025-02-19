import { PropsWithChildren } from "react";
import { LayoutContainer, LayoutHeader, LayoutMainContainer, LayoutSideNavContainer } from "./styles";
import { SideNav } from "../SideNav/SideNav";
import { IconSize, IconType } from "../Icon/types";
import { routes } from "../../../src/routing/routes";
import { Icon } from "../Icon/Icon";
import { InlineChildren } from "../InlineChildren/InlineChildren";
import { InlineChildrenAlignment, InlineChildrenSize } from "../InlineChildren/types";

export type LayoutProps = {
    title?: string,
    subtitle?: string,
    icon?: IconType,
} & PropsWithChildren

export const Layout: React.FC<LayoutProps> = ({ title, subtitle, icon, children }) => {
    return (
        <LayoutContainer>
            <LayoutSideNavContainer>
                <SideNav routes={routes} />
            </LayoutSideNavContainer>
            <LayoutHeader>
                <InlineChildren alignment={InlineChildrenAlignment.Center} size={InlineChildrenSize.xSmall}>
                <Icon type={IconType.DemonEmoji} size={IconSize.Large}/>
                {title}
                {subtitle}
                </InlineChildren>
            </LayoutHeader>
            <LayoutMainContainer>
                {children}
            </LayoutMainContainer>
        </LayoutContainer>
    );
}