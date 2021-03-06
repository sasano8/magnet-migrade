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


import * as runtime from '../runtime';
import {
    CreateTradeBot,
    CreateTradeBotFromJSON,
    CreateTradeBotToJSON,
    DummyCreate,
    DummyCreateFromJSON,
    DummyCreateToJSON,
    DummyPatch,
    DummyPatchFromJSON,
    DummyPatchToJSON,
    HTTPValidationError,
    HTTPValidationErrorFromJSON,
    HTTPValidationErrorToJSON,
    ModifyPassword,
    ModifyPasswordFromJSON,
    ModifyPasswordToJSON,
    RegisterFirstAdmin,
    RegisterFirstAdminFromJSON,
    RegisterFirstAdminToJSON,
    RegisterUser,
    RegisterUserFromJSON,
    RegisterUserToJSON,
    Token,
    TokenFromJSON,
    TokenToJSON,
    User,
    UserFromJSON,
    UserToJSON,
} from '../models';

export interface CopyScaffoldIdCopyPostRequest {
    id: number;
}

export interface CreateBotBotProfilePostRequest {
    createTradeBot: CreateTradeBot;
}

export interface CreateScaffoldPostRequest {
    dummyCreate: DummyCreate;
}

export interface DealBotBotProfileProfileIdDealGetRequest {
    profileId: number;
}

export interface DeleteScaffoldIdDeleteDeleteRequest {
    id: number;
}

export interface DeleteUserUsersUserUserIdDeleteRequest {
    userId: number;
}

export interface GetBotBotProfileProfileIdGetRequest {
    profileId: number;
}

export interface GetScaffoldIdGetRequest {
    id: number;
}

export interface GetStatisticsSystemStatisticsGetRequest {
    filterModule?: string;
}

export interface GetUserUsersUserIdGetRequest {
    userId: number;
}

export interface IndexScaffoldGetRequest {
    from?: number;
    limit?: number;
}

export interface JsonToPydanticDevelopJsonToPydanticPostRequest {
    json?: string;
}

export interface LoginUserGuestLoginPostRequest {
    password: string;
    username: string;
    clientId?: string;
    clientSecret?: string;
    grantType?: string;
    scope?: string;
}

export interface ModifyPasswordMeMeModifyPasswordPatchRequest {
    modifyPassword: ModifyPassword;
}

export interface PatchScaffoldIdPatchPatchRequest {
    id: number;
    dummyPatch: DummyPatch;
}

export interface QueryUserUsersGetRequest {
    from?: number;
    limit?: number;
}

export interface RegisterFirstAdminGuestRegisterFirstAdminPostRequest {
    registerFirstAdmin: RegisterFirstAdmin;
}

export interface RegisterUserGuestRegisterPostRequest {
    registerUser: RegisterUser;
}

export interface RequirementDefinitionSystemRequirementDefinitionGetRequest {
    domain?: string;
    timezone?: string;
    hasTimezone?: boolean;
    mostOldYear?: number;
    scraping?: boolean;
    etl?: boolean;
}

export interface SwitchBotBotProfileProfileIdSwitchPostRequest {
    profileId: number;
    isActive: boolean;
}

/**
 * 
 */
export class DefaultApi extends runtime.BaseAPI {

    /**
     * Copy
     */
    async copyScaffoldIdCopyPostRaw(requestParameters: CopyScaffoldIdCopyPostRequest): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.id === null || requestParameters.id === undefined) {
            throw new runtime.RequiredError('id','Required parameter requestParameters.id was null or undefined when calling copyScaffoldIdCopyPost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/scaffold/{id}/copy`.replace(`{${"id"}}`, encodeURIComponent(String(requestParameters.id))),
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Copy
     */
    async copyScaffoldIdCopyPost(requestParameters: CopyScaffoldIdCopyPostRequest): Promise<any> {
        const response = await this.copyScaffoldIdCopyPostRaw(requestParameters);
        return await response.value();
    }

    /**
     * Create Bot
     */
    async createBotBotProfilePostRaw(requestParameters: CreateBotBotProfilePostRequest): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.createTradeBot === null || requestParameters.createTradeBot === undefined) {
            throw new runtime.RequiredError('createTradeBot','Required parameter requestParameters.createTradeBot was null or undefined when calling createBotBotProfilePost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        const response = await this.request({
            path: `/bot/profile`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: CreateTradeBotToJSON(requestParameters.createTradeBot),
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Create Bot
     */
    async createBotBotProfilePost(requestParameters: CreateBotBotProfilePostRequest): Promise<any> {
        const response = await this.createBotBotProfilePostRaw(requestParameters);
        return await response.value();
    }

    /**
     * Create
     */
    async createScaffoldPostRaw(requestParameters: CreateScaffoldPostRequest): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.dummyCreate === null || requestParameters.dummyCreate === undefined) {
            throw new runtime.RequiredError('dummyCreate','Required parameter requestParameters.dummyCreate was null or undefined when calling createScaffoldPost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        const response = await this.request({
            path: `/scaffold/`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: DummyCreateToJSON(requestParameters.dummyCreate),
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Create
     */
    async createScaffoldPost(requestParameters: CreateScaffoldPostRequest): Promise<any> {
        const response = await this.createScaffoldPostRaw(requestParameters);
        return await response.value();
    }

    /**
     * BOT???????????????????????????????????????
     * Deal Bot
     */
    async dealBotBotProfileProfileIdDealGetRaw(requestParameters: DealBotBotProfileProfileIdDealGetRequest): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.profileId === null || requestParameters.profileId === undefined) {
            throw new runtime.RequiredError('profileId','Required parameter requestParameters.profileId was null or undefined when calling dealBotBotProfileProfileIdDealGet.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/bot/profile/{profile_id}/deal`.replace(`{${"profile_id"}}`, encodeURIComponent(String(requestParameters.profileId))),
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * BOT???????????????????????????????????????
     * Deal Bot
     */
    async dealBotBotProfileProfileIdDealGet(requestParameters: DealBotBotProfileProfileIdDealGetRequest): Promise<any> {
        const response = await this.dealBotBotProfileProfileIdDealGetRaw(requestParameters);
        return await response.value();
    }

    /**
     * Delete
     */
    async deleteScaffoldIdDeleteDeleteRaw(requestParameters: DeleteScaffoldIdDeleteDeleteRequest): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.id === null || requestParameters.id === undefined) {
            throw new runtime.RequiredError('id','Required parameter requestParameters.id was null or undefined when calling deleteScaffoldIdDeleteDelete.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/scaffold/{id}/delete`.replace(`{${"id"}}`, encodeURIComponent(String(requestParameters.id))),
            method: 'DELETE',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Delete
     */
    async deleteScaffoldIdDeleteDelete(requestParameters: DeleteScaffoldIdDeleteDeleteRequest): Promise<any> {
        const response = await this.deleteScaffoldIdDeleteDeleteRaw(requestParameters);
        return await response.value();
    }

    /**
     * Delete User
     */
    async deleteUserUsersUserUserIdDeleteRaw(requestParameters: DeleteUserUsersUserUserIdDeleteRequest): Promise<runtime.ApiResponse<number>> {
        if (requestParameters.userId === null || requestParameters.userId === undefined) {
            throw new runtime.RequiredError('userId','Required parameter requestParameters.userId was null or undefined when calling deleteUserUsersUserUserIdDelete.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            // oauth required
            if (typeof this.configuration.accessToken === 'function') {
                headerParameters["Authorization"] = this.configuration.accessToken("OAuth2PasswordBearer", []);
            } else {
                headerParameters["Authorization"] = this.configuration.accessToken;
            }
        }

        const response = await this.request({
            path: `/users/user/{user_id}`.replace(`{${"user_id"}}`, encodeURIComponent(String(requestParameters.userId))),
            method: 'DELETE',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Delete User
     */
    async deleteUserUsersUserUserIdDelete(requestParameters: DeleteUserUsersUserUserIdDeleteRequest): Promise<number> {
        const response = await this.deleteUserUsersUserUserIdDeleteRaw(requestParameters);
        return await response.value();
    }

    /**
     * Get Bot
     */
    async getBotBotProfileProfileIdGetRaw(requestParameters: GetBotBotProfileProfileIdGetRequest): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.profileId === null || requestParameters.profileId === undefined) {
            throw new runtime.RequiredError('profileId','Required parameter requestParameters.profileId was null or undefined when calling getBotBotProfileProfileIdGet.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/bot/profile/{profile_id}`.replace(`{${"profile_id"}}`, encodeURIComponent(String(requestParameters.profileId))),
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Get Bot
     */
    async getBotBotProfileProfileIdGet(requestParameters: GetBotBotProfileProfileIdGetRequest): Promise<any> {
        const response = await this.getBotBotProfileProfileIdGetRaw(requestParameters);
        return await response.value();
    }

    /**
     * Get Capabilities
     */
    async getCapabilitiesBotCapabilityGetRaw(): Promise<runtime.ApiResponse<any>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/bot/capability`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Get Capabilities
     */
    async getCapabilitiesBotCapabilityGet(): Promise<any> {
        const response = await this.getCapabilitiesBotCapabilityGetRaw();
        return await response.value();
    }

    /**
     * Get Me If Admin Or Power
     */
    async getMeIfAdminOrPowerMeAdminOrPowerGetRaw(): Promise<runtime.ApiResponse<User>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            // oauth required
            if (typeof this.configuration.accessToken === 'function') {
                headerParameters["Authorization"] = this.configuration.accessToken("OAuth2PasswordBearer", []);
            } else {
                headerParameters["Authorization"] = this.configuration.accessToken;
            }
        }

        const response = await this.request({
            path: `/me/admin_or_power`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => UserFromJSON(jsonValue));
    }

    /**
     * Get Me If Admin Or Power
     */
    async getMeIfAdminOrPowerMeAdminOrPowerGet(): Promise<User> {
        const response = await this.getMeIfAdminOrPowerMeAdminOrPowerGetRaw();
        return await response.value();
    }

    /**
     * Get Me
     */
    async getMeMeGetRaw(): Promise<runtime.ApiResponse<User>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            // oauth required
            if (typeof this.configuration.accessToken === 'function') {
                headerParameters["Authorization"] = this.configuration.accessToken("OAuth2PasswordBearer", ["me", "me"]);
            } else {
                headerParameters["Authorization"] = this.configuration.accessToken;
            }
        }

        const response = await this.request({
            path: `/me/`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => UserFromJSON(jsonValue));
    }

    /**
     * Get Me
     */
    async getMeMeGet(): Promise<User> {
        const response = await this.getMeMeGetRaw();
        return await response.value();
    }

    /**
     * Get
     */
    async getScaffoldIdGetRaw(requestParameters: GetScaffoldIdGetRequest): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.id === null || requestParameters.id === undefined) {
            throw new runtime.RequiredError('id','Required parameter requestParameters.id was null or undefined when calling getScaffoldIdGet.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/scaffold/{id}`.replace(`{${"id"}}`, encodeURIComponent(String(requestParameters.id))),
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Get
     */
    async getScaffoldIdGet(requestParameters: GetScaffoldIdGetRequest): Promise<any> {
        const response = await this.getScaffoldIdGetRaw(requestParameters);
        return await response.value();
    }

    /**
     * Get Statistics
     */
    async getStatisticsSystemStatisticsGetRaw(requestParameters: GetStatisticsSystemStatisticsGetRequest): Promise<runtime.ApiResponse<any>> {
        const queryParameters: any = {};

        if (requestParameters.filterModule !== undefined) {
            queryParameters['filter_module'] = requestParameters.filterModule;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/system/statistics`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Get Statistics
     */
    async getStatisticsSystemStatisticsGet(requestParameters: GetStatisticsSystemStatisticsGetRequest): Promise<any> {
        const response = await this.getStatisticsSystemStatisticsGetRaw(requestParameters);
        return await response.value();
    }

    /**
     * Get User
     */
    async getUserUsersUserIdGetRaw(requestParameters: GetUserUsersUserIdGetRequest): Promise<runtime.ApiResponse<User>> {
        if (requestParameters.userId === null || requestParameters.userId === undefined) {
            throw new runtime.RequiredError('userId','Required parameter requestParameters.userId was null or undefined when calling getUserUsersUserIdGet.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            // oauth required
            if (typeof this.configuration.accessToken === 'function') {
                headerParameters["Authorization"] = this.configuration.accessToken("OAuth2PasswordBearer", []);
            } else {
                headerParameters["Authorization"] = this.configuration.accessToken;
            }
        }

        const response = await this.request({
            path: `/users/{user_id}`.replace(`{${"user_id"}}`, encodeURIComponent(String(requestParameters.userId))),
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => UserFromJSON(jsonValue));
    }

    /**
     * Get User
     */
    async getUserUsersUserIdGet(requestParameters: GetUserUsersUserIdGetRequest): Promise<User> {
        const response = await this.getUserUsersUserIdGetRaw(requestParameters);
        return await response.value();
    }

    /**
     * Index
     */
    async indexScaffoldGetRaw(requestParameters: IndexScaffoldGetRequest): Promise<runtime.ApiResponse<any>> {
        const queryParameters: any = {};

        if (requestParameters.from !== undefined) {
            queryParameters['from'] = requestParameters.from;
        }

        if (requestParameters.limit !== undefined) {
            queryParameters['limit'] = requestParameters.limit;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/scaffold/`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Index
     */
    async indexScaffoldGet(requestParameters: IndexScaffoldGetRequest): Promise<any> {
        const response = await this.indexScaffoldGetRaw(requestParameters);
        return await response.value();
    }

    /**
     * Json To Pydantic
     */
    async jsonToPydanticDevelopJsonToPydanticPostRaw(requestParameters: JsonToPydanticDevelopJsonToPydanticPostRequest): Promise<runtime.ApiResponse<string>> {
        const queryParameters: any = {};

        if (requestParameters.json !== undefined) {
            queryParameters['json'] = requestParameters.json;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/develop/json_to_pydantic`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Json To Pydantic
     */
    async jsonToPydanticDevelopJsonToPydanticPost(requestParameters: JsonToPydanticDevelopJsonToPydanticPostRequest): Promise<string> {
        const response = await this.jsonToPydanticDevelopJsonToPydanticPostRaw(requestParameters);
        return await response.value();
    }

    /**
     * Load All
     */
    async loadAllBotEtlLoadAllPostRaw(): Promise<runtime.ApiResponse<any>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/bot/etl/load_all`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Load All
     */
    async loadAllBotEtlLoadAllPost(): Promise<any> {
        const response = await this.loadAllBotEtlLoadAllPostRaw();
        return await response.value();
    }

    /**
     * Login User
     */
    async loginUserGuestLoginPostRaw(requestParameters: LoginUserGuestLoginPostRequest): Promise<runtime.ApiResponse<Token>> {
        if (requestParameters.password === null || requestParameters.password === undefined) {
            throw new runtime.RequiredError('password','Required parameter requestParameters.password was null or undefined when calling loginUserGuestLoginPost.');
        }

        if (requestParameters.username === null || requestParameters.username === undefined) {
            throw new runtime.RequiredError('username','Required parameter requestParameters.username was null or undefined when calling loginUserGuestLoginPost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const consumes: runtime.Consume[] = [
            { contentType: 'application/x-www-form-urlencoded' },
        ];
        // @ts-ignore: canConsumeForm may be unused
        const canConsumeForm = runtime.canConsumeForm(consumes);

        let formParams: { append(param: string, value: any): any };
        let useForm = false;
        if (useForm) {
            formParams = new FormData();
        } else {
            formParams = new URLSearchParams();
        }

        if (requestParameters.clientId !== undefined) {
            formParams.append('client_id', requestParameters.clientId as any);
        }

        if (requestParameters.clientSecret !== undefined) {
            formParams.append('client_secret', requestParameters.clientSecret as any);
        }

        if (requestParameters.grantType !== undefined) {
            formParams.append('grant_type', requestParameters.grantType as any);
        }

        if (requestParameters.password !== undefined) {
            formParams.append('password', requestParameters.password as any);
        }

        if (requestParameters.scope !== undefined) {
            formParams.append('scope', requestParameters.scope as any);
        }

        if (requestParameters.username !== undefined) {
            formParams.append('username', requestParameters.username as any);
        }

        const response = await this.request({
            path: `/guest/login`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: formParams,
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => TokenFromJSON(jsonValue));
    }

    /**
     * Login User
     */
    async loginUserGuestLoginPost(requestParameters: LoginUserGuestLoginPostRequest): Promise<Token> {
        const response = await this.loginUserGuestLoginPostRaw(requestParameters);
        return await response.value();
    }

    /**
     * Logout Me
     */
    async logoutMeMeLogoutPostRaw(): Promise<runtime.ApiResponse<any>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            // oauth required
            if (typeof this.configuration.accessToken === 'function') {
                headerParameters["Authorization"] = this.configuration.accessToken("OAuth2PasswordBearer", []);
            } else {
                headerParameters["Authorization"] = this.configuration.accessToken;
            }
        }

        const response = await this.request({
            path: `/me/logout`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Logout Me
     */
    async logoutMeMeLogoutPost(): Promise<any> {
        const response = await this.logoutMeMeLogoutPostRaw();
        return await response.value();
    }

    /**
     * Modify Password Me
     */
    async modifyPasswordMeMeModifyPasswordPatchRaw(requestParameters: ModifyPasswordMeMeModifyPasswordPatchRequest): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.modifyPassword === null || requestParameters.modifyPassword === undefined) {
            throw new runtime.RequiredError('modifyPassword','Required parameter requestParameters.modifyPassword was null or undefined when calling modifyPasswordMeMeModifyPasswordPatch.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        if (this.configuration && this.configuration.accessToken) {
            // oauth required
            if (typeof this.configuration.accessToken === 'function') {
                headerParameters["Authorization"] = this.configuration.accessToken("OAuth2PasswordBearer", ["me", "me"]);
            } else {
                headerParameters["Authorization"] = this.configuration.accessToken;
            }
        }

        const response = await this.request({
            path: `/me/modify_password`,
            method: 'PATCH',
            headers: headerParameters,
            query: queryParameters,
            body: ModifyPasswordToJSON(requestParameters.modifyPassword),
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Modify Password Me
     */
    async modifyPasswordMeMeModifyPasswordPatch(requestParameters: ModifyPasswordMeMeModifyPasswordPatchRequest): Promise<any> {
        const response = await this.modifyPasswordMeMeModifyPasswordPatchRaw(requestParameters);
        return await response.value();
    }

    /**
     * Patch
     */
    async patchScaffoldIdPatchPatchRaw(requestParameters: PatchScaffoldIdPatchPatchRequest): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.id === null || requestParameters.id === undefined) {
            throw new runtime.RequiredError('id','Required parameter requestParameters.id was null or undefined when calling patchScaffoldIdPatchPatch.');
        }

        if (requestParameters.dummyPatch === null || requestParameters.dummyPatch === undefined) {
            throw new runtime.RequiredError('dummyPatch','Required parameter requestParameters.dummyPatch was null or undefined when calling patchScaffoldIdPatchPatch.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        const response = await this.request({
            path: `/scaffold/{id}/patch`.replace(`{${"id"}}`, encodeURIComponent(String(requestParameters.id))),
            method: 'PATCH',
            headers: headerParameters,
            query: queryParameters,
            body: DummyPatchToJSON(requestParameters.dummyPatch),
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Patch
     */
    async patchScaffoldIdPatchPatch(requestParameters: PatchScaffoldIdPatchPatchRequest): Promise<any> {
        const response = await this.patchScaffoldIdPatchPatchRaw(requestParameters);
        return await response.value();
    }

    /**
     * Query User
     */
    async queryUserUsersGetRaw(requestParameters: QueryUserUsersGetRequest): Promise<runtime.ApiResponse<Array<User>>> {
        const queryParameters: any = {};

        if (requestParameters.from !== undefined) {
            queryParameters['from'] = requestParameters.from;
        }

        if (requestParameters.limit !== undefined) {
            queryParameters['limit'] = requestParameters.limit;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            // oauth required
            if (typeof this.configuration.accessToken === 'function') {
                headerParameters["Authorization"] = this.configuration.accessToken("OAuth2PasswordBearer", []);
            } else {
                headerParameters["Authorization"] = this.configuration.accessToken;
            }
        }

        const response = await this.request({
            path: `/users/`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => jsonValue.map(UserFromJSON));
    }

    /**
     * Query User
     */
    async queryUserUsersGet(requestParameters: QueryUserUsersGetRequest): Promise<Array<User>> {
        const response = await this.queryUserUsersGetRaw(requestParameters);
        return await response.value();
    }

    /**
     * ???????????????????????????????????????????????????????????????????????????????????????
     * Register First Admin
     */
    async registerFirstAdminGuestRegisterFirstAdminPostRaw(requestParameters: RegisterFirstAdminGuestRegisterFirstAdminPostRequest): Promise<runtime.ApiResponse<User>> {
        if (requestParameters.registerFirstAdmin === null || requestParameters.registerFirstAdmin === undefined) {
            throw new runtime.RequiredError('registerFirstAdmin','Required parameter requestParameters.registerFirstAdmin was null or undefined when calling registerFirstAdminGuestRegisterFirstAdminPost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        const response = await this.request({
            path: `/guest/register_first_admin`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: RegisterFirstAdminToJSON(requestParameters.registerFirstAdmin),
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => UserFromJSON(jsonValue));
    }

    /**
     * ???????????????????????????????????????????????????????????????????????????????????????
     * Register First Admin
     */
    async registerFirstAdminGuestRegisterFirstAdminPost(requestParameters: RegisterFirstAdminGuestRegisterFirstAdminPostRequest): Promise<User> {
        const response = await this.registerFirstAdminGuestRegisterFirstAdminPostRaw(requestParameters);
        return await response.value();
    }

    /**
     * Register User
     */
    async registerUserGuestRegisterPostRaw(requestParameters: RegisterUserGuestRegisterPostRequest): Promise<runtime.ApiResponse<User>> {
        if (requestParameters.registerUser === null || requestParameters.registerUser === undefined) {
            throw new runtime.RequiredError('registerUser','Required parameter requestParameters.registerUser was null or undefined when calling registerUserGuestRegisterPost.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        headerParameters['Content-Type'] = 'application/json';

        const response = await this.request({
            path: `/guest/register`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: RegisterUserToJSON(requestParameters.registerUser),
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => UserFromJSON(jsonValue));
    }

    /**
     * Register User
     */
    async registerUserGuestRegisterPost(requestParameters: RegisterUserGuestRegisterPostRequest): Promise<User> {
        const response = await this.registerUserGuestRegisterPostRaw(requestParameters);
        return await response.value();
    }

    /**
     * Requirement Definition
     */
    async requirementDefinitionSystemRequirementDefinitionGetRaw(requestParameters: RequirementDefinitionSystemRequirementDefinitionGetRequest): Promise<runtime.ApiResponse<any>> {
        const queryParameters: any = {};

        if (requestParameters.domain !== undefined) {
            queryParameters['domain'] = requestParameters.domain;
        }

        if (requestParameters.timezone !== undefined) {
            queryParameters['timezone'] = requestParameters.timezone;
        }

        if (requestParameters.hasTimezone !== undefined) {
            queryParameters['has_timezone'] = requestParameters.hasTimezone;
        }

        if (requestParameters.mostOldYear !== undefined) {
            queryParameters['most_old_year'] = requestParameters.mostOldYear;
        }

        if (requestParameters.scraping !== undefined) {
            queryParameters['scraping'] = requestParameters.scraping;
        }

        if (requestParameters.etl !== undefined) {
            queryParameters['etl'] = requestParameters.etl;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/system/requirement_definition`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Requirement Definition
     */
    async requirementDefinitionSystemRequirementDefinitionGet(requestParameters: RequirementDefinitionSystemRequirementDefinitionGetRequest): Promise<any> {
        const response = await this.requirementDefinitionSystemRequirementDefinitionGetRaw(requestParameters);
        return await response.value();
    }

    /**
     * Root
     */
    async rootGetRaw(): Promise<runtime.ApiResponse<string>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Root
     */
    async rootGet(): Promise<string> {
        const response = await this.rootGetRaw();
        return await response.value();
    }

    /**
     * Bot???OnOff????????????????????????
     * Switch Bot
     */
    async switchBotBotProfileProfileIdSwitchPostRaw(requestParameters: SwitchBotBotProfileProfileIdSwitchPostRequest): Promise<runtime.ApiResponse<any>> {
        if (requestParameters.profileId === null || requestParameters.profileId === undefined) {
            throw new runtime.RequiredError('profileId','Required parameter requestParameters.profileId was null or undefined when calling switchBotBotProfileProfileIdSwitchPost.');
        }

        if (requestParameters.isActive === null || requestParameters.isActive === undefined) {
            throw new runtime.RequiredError('isActive','Required parameter requestParameters.isActive was null or undefined when calling switchBotBotProfileProfileIdSwitchPost.');
        }

        const queryParameters: any = {};

        if (requestParameters.isActive !== undefined) {
            queryParameters['is_active'] = requestParameters.isActive;
        }

        const headerParameters: runtime.HTTPHeaders = {};

        const response = await this.request({
            path: `/bot/profile/{profile_id}/switch`.replace(`{${"profile_id"}}`, encodeURIComponent(String(requestParameters.profileId))),
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Bot???OnOff????????????????????????
     * Switch Bot
     */
    async switchBotBotProfileProfileIdSwitchPost(requestParameters: SwitchBotBotProfileProfileIdSwitchPostRequest): Promise<any> {
        const response = await this.switchBotBotProfileProfileIdSwitchPostRaw(requestParameters);
        return await response.value();
    }

    /**
     * Withdraw Me
     */
    async withdrawMeMeDeleteRaw(): Promise<runtime.ApiResponse<number>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && this.configuration.accessToken) {
            // oauth required
            if (typeof this.configuration.accessToken === 'function') {
                headerParameters["Authorization"] = this.configuration.accessToken("OAuth2PasswordBearer", ["me", "me"]);
            } else {
                headerParameters["Authorization"] = this.configuration.accessToken;
            }
        }

        const response = await this.request({
            path: `/me/`,
            method: 'DELETE',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.TextApiResponse(response) as any;
    }

    /**
     * Withdraw Me
     */
    async withdrawMeMeDelete(): Promise<number> {
        const response = await this.withdrawMeMeDeleteRaw();
        return await response.value();
    }

}
