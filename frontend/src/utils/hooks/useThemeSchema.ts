import { useEffect, useCallback, useRef } from 'react'
import { useThemeStore } from '@/store/themeStore'
import presetThemeSchemaConfig from '@/configs/preset-theme-schema.config'

export type ThemeVariables = Record<
    'primary' | 'primaryDeep' | 'primaryMild' | 'primarySubtle' | 'neutral',
    string
>

export interface MappedTheme {
    [key: string]: string
}

export const mapTheme = (variables: ThemeVariables): MappedTheme => {
    return {
        '--primary': variables.primary || '',
        '--primary-deep': variables.primaryDeep || '',
        '--primary-mild': variables.primaryMild || '',
        '--primary-subtle': variables.primarySubtle || '',
        '--neutral': variables.neutral || '',
    }
}

function useThemeSchema() {
    const themeSchema = useThemeStore((state) => state.themeSchema)
    const mode = useThemeStore((state) => state.mode)
    const lastAppliedTheme = useRef<string>('')

    const applyTheme = useCallback((theme: string): void => {
        // Prevent applying the same theme multiple times
        if (lastAppliedTheme.current === theme) {
            return
        }

        if (presetThemeSchemaConfig[theme] && presetThemeSchemaConfig[theme][mode]) {
            const themeObject = mapTheme(presetThemeSchemaConfig[theme][mode])
            if (!themeObject) return

            const root = document.documentElement

            Object.keys(themeObject).forEach((property) => {
                if (property === 'name') {
                    return
                }

                root.style.setProperty(property, themeObject[property])
            })

            lastAppliedTheme.current = theme
        }
    }, [mode])

    useEffect(() => {
        if (themeSchema && themeSchema !== lastAppliedTheme.current) {
            applyTheme(themeSchema)
        }
    }, [themeSchema, applyTheme])
}

export default useThemeSchema
