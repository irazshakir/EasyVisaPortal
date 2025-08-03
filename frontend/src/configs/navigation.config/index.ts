import {
    NAV_ITEM_TYPE_TITLE,
    NAV_ITEM_TYPE_ITEM,
    NAV_ITEM_TYPE_COLLAPSE,
} from '@/constants/navigation.constant'

import type { NavigationTree } from '@/@types/navigation'

const navigationConfig: NavigationTree[] = [
    {
        key: 'dashboard',
        path: '/dashboard',
        title: 'Dashboard',
        translateKey: 'nav.dashboard',
        icon: 'dashboard',
        type: NAV_ITEM_TYPE_ITEM,
        roles: ['admin', 'department_head', 'manager', 'team_lead', 'consultant', 'support'],
        subMenu: [],
    },
    {
        key: 'leads',
        path: '/leads',
        title: 'Leads',
        translateKey: 'nav.leads',
        icon: 'leads',
        type: NAV_ITEM_TYPE_ITEM,
        roles: ['admin', 'department_head', 'manager', 'team_lead', 'consultant', 'support'],
        subMenu: [],
    },
    {
        key: 'chats',
        path: '/chats',
        title: 'Chats',
        translateKey: 'nav.chats',
        icon: 'chats',
        type: NAV_ITEM_TYPE_ITEM,
        roles: ['admin'],
        subMenu: [],
    },
    {
        key: 'reports',
        path: '/reports',
        title: 'Reports',
        translateKey: 'nav.reports',
        icon: 'reports',
        type: NAV_ITEM_TYPE_ITEM,
        roles: ['admin'],
        subMenu: [],
    },
    {
        key: 'users',
        path: '/users',
        title: 'Users',
        translateKey: 'nav.users',
        icon: 'users',
        type: NAV_ITEM_TYPE_ITEM,
        roles: ['admin'],
        subMenu: [],
    },
    {
        key: 'organization',
        path: '/organization',
        title: 'Organization',
        translateKey: 'nav.organization',
        icon: 'organization',
        type: NAV_ITEM_TYPE_COLLAPSE,
        roles: ['admin'],
        authority: [],
        subMenu: [
            {
                key: 'departments',
                path: '/departments',
                title: 'Departments',
                translateKey: 'nav.departments',
                icon: 'departments',
                type: NAV_ITEM_TYPE_ITEM,
                authority: [],
                subMenu: [],
            },
            {
                key: 'products',
                path: '/products',
                title: 'Products',
                translateKey: 'nav.products',
                icon: 'products',
                type: NAV_ITEM_TYPE_ITEM,
                authority: [],
                subMenu: [],
            },
            {
                key: 'status',
                path: '/status',
                title: 'Status',
                translateKey: 'nav.status',
                icon: 'status',
                type: NAV_ITEM_TYPE_ITEM,
                authority: [],
                subMenu: [],
            },
        ],
    }
]

export default navigationConfig
