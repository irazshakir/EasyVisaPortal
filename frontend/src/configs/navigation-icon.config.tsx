import {
    PiChartLineUpDuotone,
    PiFunnelDuotone,
    PiChatCircleTextDuotone,
    PiPackageDuotone,
    PiUsersDuotone,
    PiGearSixDuotone,
    PiBuildingsDuotone,
    PiUsersThreeDuotone,
    PiFileTextDuotone,
} from 'react-icons/pi'
import type { JSX } from 'react'

export type NavigationIcons = Record<string, JSX.Element>

const navigationIcon: NavigationIcons = {
    dashboard: <PiChartLineUpDuotone />,
    leads: <PiFunnelDuotone />,
    chats: <PiChatCircleTextDuotone />,
    products: <PiPackageDuotone />,
    users: <PiUsersDuotone />,
    settings: <PiGearSixDuotone />,
    organization: <PiBuildingsDuotone />,
    departments: <PiUsersDuotone />,
    teams: <PiUsersThreeDuotone />,
    reports: <PiFileTextDuotone />,
}

export default navigationIcon
