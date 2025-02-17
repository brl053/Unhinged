import { AthenaRoute } from "../../../src/routing/routes";
import { Icon } from "../Icon/Icon";
import { IconSize, IconType } from "../Icon/types";
import { SideNavBodyContainer, SideNavContainer, SideNavFooterContainer, SideNavHeaderContainer } from "./styles";

type SideNavProps = {
    // TODO: Use an <IconButton /> component
    routes: AthenaRoute[];
    // trailing: React.ReactNode;
    // isCollapsed: boolean;
    // activeItemId: string;
    // onActiveItemChange: (id: string) => void;
}

export const SideNav: React.FC<SideNavProps> = ({
    routes,
    // trailing,
    // isCollapsed,
    // activeItemId,
    // onActiveItemChange,
}) => {
    return (
        <SideNavContainer>
            <SideNavHeaderContainer>
            </SideNavHeaderContainer>
            <SideNavBodyContainer>
                {routes.map((route) => <Icon size={IconSize.Medium} type={route.icon} />)}
            </SideNavBodyContainer>
            <SideNavFooterContainer>
                
            </SideNavFooterContainer>
        </SideNavContainer>
    )
}