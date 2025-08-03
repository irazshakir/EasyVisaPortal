import { lazy } from 'react'
import authRoute from './authRoute'
import othersRoute from './othersRoute'
import type { Routes } from '@/@types/routes'

export const publicRoutes: Routes = [
    {
        key: 'home',
        path: '/',
        component: lazy(() => import('@/views/pages/HomePage')),
        authority: [],
    },
    {
        key: 'signIn',
        path: '/sign-in',
        component: lazy(() => import('@/views/auth/SignIn')),
        authority: [],
    },
    {
        key: 'signUp',
        path: '/sign-up',
        component: lazy(() => import('@/views/auth/SignUp')),
        authority: [],
    },
    {
        key: 'forgotPassword',
        path: '/forgot-password',
        component: lazy(() => import('@/views/auth/ForgotPassword')),
        authority: [],
    },
    {
        key: 'resetPassword',
        path: '/reset-password',
        component: lazy(() => import('@/views/auth/ResetPassword')),
        authority: [],
    },
    ...authRoute,
]

export const protectedRoutes: Routes = [
    {
        key: 'dashboard',
        path: '/dashboard',
        component: lazy(() => import('@/views/pages/Dashboard')),
        authority: [],
    },
    {
        key: 'chats',
        path: '/chats',
        component: lazy(() => import('@/views/pages/Chats')),
        authority: [],
    },
    {
        key: 'reports',
        path: '/reports',
        component: lazy(() => import('@/views/pages/Reports/Reports')),
        authority: [],
    },
    {
        key: 'users',
        path: '/users',
        component: lazy(() => import('@/views/pages/Users/Users')),
        authority: [],
    },
    {
        key: 'users.new',
        path: '/users/new',
        component: lazy(() => import('@/views/pages/Users/AddUser')),
        authority: [],
    },
    {
        key: 'users.edit',
        path: '/users/:id/edit',
        component: lazy(() => import('@/views/pages/Users/EditUser')),
        authority: [],
    },
    {
        key: 'departments',
        path: '/departments',
        component: lazy(() => import('@/views/pages/Departments/Departments')),
        authority: [],
    },
    {
        key: 'departments.new',
        path: '/departments/new',
        component: lazy(() => import('@/views/pages/Departments/AddDepartment')),
        authority: [],
    },
    // {
    //     key: 'departments.edit',
    //     path: '/departments/:id/edit',
    //     component: lazy(() => import('@/views/pages/Departments/EditDepartment')),
    //     authority: [],
    // },
    {
        key: 'products',
        path: '/products',
        component: lazy(() => import('@/views/pages/Products/Products')),
        authority: [],
    },
    {
        key: 'products.new',
        path: '/products/new',
        component: lazy(() => import('@/views/pages/Products/AddProduct')),
        authority: [],
    },
    {
        key: 'products.edit',
        path: '/products/:id/edit',
        component: lazy(() => import('@/views/pages/Products/EditProduct')),
        authority: [],
    },
    {
        key: 'status',
        path: '/status',
        component: lazy(() => import('@/views/pages/Status/Status')),
        authority: [],
    },
    {
        key: 'status.new',
        path: '/status/new',
        component: lazy(() => import('@/views/pages/Status/AddStatus')),
        authority: [],
    },
    {
        key: 'status.edit',
        path: '/status/:id/edit',
        component: lazy(() => import('@/views/pages/Status/EditStatus')),
        authority: [],
    },
    {
        key: 'leads',
        path: '/leads',
        component: lazy(() => import('@/views/pages/Leads/Leads')),
        authority: [],
    },
    {
        key: 'leads.new',
        path: '/leads/new',
        component: lazy(() => import('@/views/pages/Leads/AddLead')),
        authority: [],
    },
    {
        key: 'leads.edit',
        path: '/leads/:id/edit',
        component: lazy(() => import('@/views/pages/Leads/EditLead')),
        authority: [],
    },
    ...othersRoute,
]
