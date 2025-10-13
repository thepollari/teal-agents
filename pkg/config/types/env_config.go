package types

type EnvConfig struct {
	APIKey                               string  `mapstructure:"API_KEY" validate:"required"`
	ServiceConfig                        string  `mapstructure:"SERVICE_CONFIG" validate:"required"`
	RemotePluginPath                     *string `mapstructure:"REMOTE_PLUGIN_PATH"`
	TypesModule                          *string `mapstructure:"TYPES_MODULE"`
	PluginModule                         *string `mapstructure:"PLUGIN_MODULE"`
	CustomChatCompletionFactoryModule    *string `mapstructure:"CUSTOM_CHAT_COMPLETION_FACTORY_MODULE"`
	CustomChatCompletionFactoryClassName *string `mapstructure:"CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME"`
	StructuredOutputTransformerModel     string  `mapstructure:"STRUCTURED_OUTPUT_TRANSFORMER_MODEL"`
	A2AEnabled                           string  `mapstructure:"A2A_ENABLED" validate:"required"`
	AgentBaseURL                         string  `mapstructure:"AGENT_BASE_URL" validate:"required"`
	ProviderOrg                          string  `mapstructure:"PROVIDER_ORG" validate:"required"`
	ProviderURL                          string  `mapstructure:"PROVIDER_URL" validate:"required"`
	A2AOutputClassifierModel             string  `mapstructure:"A2A_OUTPUT_CLASSIFIER_MODEL"`
	StateManagement                      string  `mapstructure:"STATE_MANAGEMENT" validate:"required"`
	AuthorizerModule                     *string `mapstructure:"AUTHORIZER_MODULE"`
	AuthorizerClass                      *string `mapstructure:"AUTHORIZER_CLASS"`
	RedisHost                            *string `mapstructure:"REDIS_HOST"`
	RedisPort                            *string `mapstructure:"REDIS_PORT"`
	RedisDB                              *string `mapstructure:"REDIS_DB"`
	RedisTTL                             *string `mapstructure:"REDIS_TTL"`
	RedisSSL                             string  `mapstructure:"REDIS_SSL"`
	RedisPwd                             *string `mapstructure:"REDIS_PWD"`
	PersistenceModule                    string  `mapstructure:"PERSISTENCE_MODULE" validate:"required"`
	PersistenceClass                     string  `mapstructure:"PERSISTENCE_CLASS" validate:"required"`
}

func DefaultEnvConfig() *EnvConfig {
	structuredOutputModel := "gpt-4o"
	a2aEnabled := "false"
	agentBaseURL := "http://localhost:8000"
	providerOrg := "My Organization"
	providerURL := "http://localhost:8000"
	a2aClassifier := "gpt-4o-mini"
	stateManagement := "in-memory"
	redisSSL := "true"
	persistenceModule := "persistence/in_memory_persistence_manager.py"
	persistenceClass := "InMemoryPersistenceManager"

	return &EnvConfig{
		ServiceConfig:                    "agents/config.yaml",
		StructuredOutputTransformerModel: structuredOutputModel,
		A2AEnabled:                       a2aEnabled,
		AgentBaseURL:                     agentBaseURL,
		ProviderOrg:                      providerOrg,
		ProviderURL:                      providerURL,
		A2AOutputClassifierModel:         a2aClassifier,
		StateManagement:                  stateManagement,
		RedisSSL:                         redisSSL,
		PersistenceModule:                persistenceModule,
		PersistenceClass:                 persistenceClass,
	}
}
