import { forwardRef, useState, useEffect, useRef } from 'react'
import classNames from 'classnames'
import { useConfig } from '../ConfigProvider'
import { useForm } from '../Form/context'
import { useInputGroup } from '../InputGroup/context'
import { CONTROL_SIZES } from '../utils/constants'
import isNil from 'lodash/isNil'
import type { CommonProps } from '../@types/common'
import type {
    InputHTMLAttributes,
    ComponentProps,
    RefObject,
} from 'react'
import type { FormikProps } from 'formik'

interface BaseInputProps {
    invalid?: boolean
    textArea?: boolean
    prefix?: React.ReactNode
    suffix?: React.ReactNode
    size?: 'lg' | 'md' | 'sm'
}

export type InputProps = BaseInputProps & 
    Omit<InputHTMLAttributes<HTMLInputElement | HTMLTextAreaElement>, 'size' | 'prefix'> & {
    field?: {
        name: string
        value: any
        onChange: (e: React.ChangeEvent<any>) => void
        onBlur: (e: React.FocusEvent<any>) => void
    }
    form?: FormikProps<any>
}

const Input = forwardRef((props: InputProps, ref) => {
    const {
        className,
        disabled,
        invalid,
        prefix,
        size,
        suffix,
        textArea,
        type = 'text',
        style,
        field,
        form,
        ...rest
    } = props

    const [prefixGutter, setPrefixGutter] = useState(0)
    const [suffixGutter, setSuffixGutter] = useState(0)

    const { controlSize, direction } = useConfig()
    const formControlSize = useForm()?.size
    const inputGroupSize = useInputGroup()?.size

    const inputSize = size || inputGroupSize || formControlSize || controlSize

    const prefixNode = useRef<HTMLDivElement>(null)
    const suffixNode = useRef<HTMLDivElement>(null)

    const getAffixSize = () => {
        if (!prefixNode.current && !suffixNode.current) {
            return
        }
        const prefixNodeWidth = prefixNode?.current?.offsetWidth
        const suffixNodeWidth = suffixNode?.current?.offsetWidth

        if (isNil(prefixNodeWidth) && isNil(suffixNodeWidth)) {
            return
        }

        if (prefixNodeWidth) {
            setPrefixGutter(prefixNodeWidth)
        }

        if (suffixNodeWidth) {
            setSuffixGutter(suffixNodeWidth)
        }
    }

    useEffect(() => {
        getAffixSize()
    }, [prefix, suffix])

    const inputClass = classNames(
        'input',
        className,
        invalid ? 'input-invalid' : '',
        `input-${inputSize}`,
        disabled && 'input-disabled'
    )

    const remToPxConvertion = (pixel: number) => 0.0625 * pixel

    const affixGutterStyle = () => {
        const leftGutter = `${remToPxConvertion(prefixGutter) + 1}rem`
        const rightGutter = `${remToPxConvertion(suffixGutter) + 1}rem`
        const gutterStyle: {
            paddingLeft?: string
            paddingRight?: string
        } = {}

        if (direction === 'ltr') {
            if (prefix) {
                gutterStyle.paddingLeft = leftGutter
            }
            if (suffix) {
                gutterStyle.paddingRight = rightGutter
            }
        }

        if (direction === 'rtl') {
            if (prefix) {
                gutterStyle.paddingRight = leftGutter
            }
            if (suffix) {
                gutterStyle.paddingLeft = rightGutter
            }
        }

        return gutterStyle
    }

    if (textArea) {
        return (
            <textarea
                ref={ref as RefObject<HTMLTextAreaElement>}
                className={inputClass}
                disabled={disabled}
                {...field}
                {...rest}
                style={{ ...style, ...affixGutterStyle() }}
            />
        )
    }

    const inputElement = (
        <input
            ref={ref as RefObject<HTMLInputElement>}
            className={inputClass}
            disabled={disabled}
            type={type}
            {...field}
            {...rest}
            style={{ ...style, ...affixGutterStyle() }}
        />
    )

    if (prefix || suffix) {
        return (
            <span className="input-wrapper">
                {prefix && (
                    <div ref={prefixNode} className="input-prefix">
                        {prefix}
                    </div>
                )}
                {inputElement}
                {suffix && (
                    <div ref={suffixNode} className="input-suffix">
                        {suffix}
                    </div>
                )}
            </span>
        )
    }

    return inputElement
})

Input.displayName = 'Input'

export default Input
