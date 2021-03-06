/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { exists, mapValues } from '../runtime';
import {
    Item,
    ItemFromJSON,
    ItemFromJSONTyped,
    ItemToJSON,
} from './';

/**
 * 
 * @export
 * @interface User
 */
export interface User {
    /**
     * 
     * @type {boolean}
     * @memberof User
     */
    disabled?: boolean;
    /**
     * 
     * @type {string}
     * @memberof User
     */
    email: string;
    /**
     * 
     * @type {string}
     * @memberof User
     */
    full_name?: string;
    /**
     * 
     * @type {number}
     * @memberof User
     */
    id: number;
    /**
     * 
     * @type {boolean}
     * @memberof User
     */
    is_active: boolean;
    /**
     * 
     * @type {Array<Item>}
     * @memberof User
     */
    items?: Array<Item>;
    /**
     * 
     * @type {string}
     * @memberof User
     */
    username: string;
}

export function UserFromJSON(json: any): User {
    return UserFromJSONTyped(json, false);
}

export function UserFromJSONTyped(json: any, ignoreDiscriminator: boolean): User {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'disabled': !exists(json, 'disabled') ? undefined : json['disabled'],
        'email': json['email'],
        'full_name': !exists(json, 'full_name') ? undefined : json['full_name'],
        'id': json['id'],
        'is_active': json['is_active'],
        'items': !exists(json, 'items') ? undefined : ((json['items'] as Array<any>).map(ItemFromJSON)),
        'username': json['username'],
    };
}

export function UserToJSON(value?: User | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'disabled': value.disabled,
        'email': value.email,
        'full_name': value.full_name,
        'id': value.id,
        'is_active': value.is_active,
        'items': value.items === undefined ? undefined : ((value.items as Array<any>).map(ItemToJSON)),
        'username': value.username,
    };
}


